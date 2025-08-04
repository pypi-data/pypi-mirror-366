import sys
import logging
import asyncio
import base64
import os
import re
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, Callable, Literal

import httpx
from mcp.server.fastmcp import FastMCP

# --- Configuration & Argument Parsing ---
parser = argparse.ArgumentParser(description="ServiceNow MCP Exporter")
parser.add_argument(
    "--instance-name", required=True, help="ServiceNow instance name (e.g., 'dev12345')"
)
parser.add_argument("--username", required=True, help="ServiceNow username")
parser.add_argument("--password", required=True, help="ServiceNow password")
# This line is important for allowing the script to run without failing on MCP's internal args
args, unknown = parser.parse_known_args()

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
log = logging.getLogger("ServiceNowMCP")

# --- MCP Server Initialization ---
mcp = FastMCP("servicenow-exporter")

# --- In-Memory Job Store ---
# This dictionary will hold the status and results of our export jobs.
export_jobs: Dict[str, Dict[str, Any]] = {}

# --- ServiceNow API Logic ---


class ServiceNowExporter:
    """Handles the logic for fetching data from ServiceNow asynchronously."""

    def __init__(self, request_id: str):
        self.base_url = f"https://{args.instance_name}.service-now.com/api/now/table"
        self.auth = httpx.BasicAuth(args.username, args.password)
        self.request_id = request_id
        self.total_records = 0

    def update_status(
        self,
        status: str,
        progress: Optional[str] = None,
        attachment: Optional[Dict] = None,
        error: Optional[str] = None,
    ):
        """Updates the job status in the global store."""
        job = export_jobs.get(self.request_id, {})
        job["status"] = status
        if progress:
            job["progress"] = progress
        if attachment:
            job["attachment"] = attachment
        if error:
            job["error"] = error
        export_jobs[self.request_id] = job
        log.info(f"Job '{self.request_id}' status updated: {status} {progress or ''}")

    async def get_total_record_count(
        self, client: httpx.AsyncClient, table: str, query: Optional[str]
    ) -> int:
        log.info(
            f"Fetching total record count for table '{table}' with query '{query}'"
        )
        params = {"sysparm_limit": 1, "sysparm_query": query if query else ""}
        try:
            response = await client.get(
                f"{self.base_url}/{table}",
                params=params,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            total_count = int(response.headers.get("X-Total-Count", 0))
            log.info(f"Found {total_count} records to export.")
            return total_count
        except httpx.HTTPStatusError as e:
            error_message = f"Error connecting to ServiceNow: HTTP {e.response.status_code}. Check instance, table name, and credentials."
            log.error(f"{error_message} - {e.response.text}")
            self.update_status("failed", error=error_message)
            raise
        except Exception as e:
            log.error(f"An unexpected error occurred during record count: {e}")
            self.update_status("failed", error=str(e))
            raise

    async def fetch_and_write_data(
        self,
        table: str,
        output_file_path: str,
        query: Optional[str],
        fields: Optional[str],
        display_value: bool,
    ):
        page_size = 5000
        offset = 0
        records_written = 0

        async with httpx.AsyncClient(auth=self.auth, timeout=120.0) as client:
            self.total_records = await self.get_total_record_count(client, table, query)
            if self.total_records == 0:
                self.update_status(
                    "complete", progress="No records found for the given query."
                )
                return

            self.update_status(
                "running",
                progress=f"Starting export of {self.total_records} records...",
            )

            with open(output_file_path, "w", newline="", encoding="utf-8") as f:
                writer = None

                while records_written < self.total_records:
                    params = {
                        "sysparm_limit": page_size,
                        "sysparm_offset": offset,
                        "sysparm_query": query if query else "ORDERBYsys_created_on",
                        "sysparm_display_value": "true" if display_value else "false",
                        "sysparm_exclude_reference_link": "true",
                    }
                    if fields:
                        params["sysparm_fields"] = fields

                    log.info(f"Fetching page: offset={offset}, limit={page_size}")
                    response = await client.get(
                        f"{self.base_url}/{table}", params=params
                    )
                    response.raise_for_status()

                    data = response.json()
                    results = data.get("result")

                    if not isinstance(results, list) or not results:
                        log.warning(
                            f"No more results found at offset {offset}. Ending export."
                        )
                        break

                    if writer is None:
                        import csv

                        headers = results[0].keys() if results else []
                        writer = csv.DictWriter(f, fieldnames=headers)
                        writer.writeheader()

                    writer.writerows(results)

                    records_written += len(results)
                    offset += page_size

                    self.update_status(
                        "running",
                        progress=f"{records_written} / {self.total_records} records exported...",
                    )

        log.info("Finished writing data to file.")


# --- The MCP Tool Definitions ---


@mcp.tool(
    description="Starts an asynchronous export job for a ServiceNow table. Use get_export_status to check progress and retrieve the file."
)
async def export_table(
    request_id: str,
    table: str,
    query: Optional[str] = None,
    fields: Optional[str] = None,
    include_display_values: bool = True,
) -> Dict[str, str]:
    """
    Starts an asynchronous export job and returns a request_id for tracking.
    """
    log.info(f"Received export request '{request_id}' for table '{table}'")

    if request_id in export_jobs:
        return {
            "request_id": request_id,
            "status": "Error: This request_id is already in use.",
        }

    # Initialize the job in the store
    export_jobs[request_id] = {"status": "pending", "progress": "Job has been queued."}

    # Start the background task
    asyncio.create_task(
        run_export_worker(
            request_id,
            table,
            query,
            fields,
            include_display_values,
        )
    )

    return {
        "request_id": request_id,
        "status": f"Acknowledged. The export for table '{table}' has been started. Use get_export_status to check progress.",
    }


@mcp.tool(
    description="Checks the status of a running export job and retrieves the file when complete."
)
async def get_export_status(request_id: str) -> Dict[str, Any]:
    """
    Checks the status of a previously started export job.
    """
    log.info(f"Received status check for request '{request_id}'")

    job = export_jobs.get(request_id)

    if not job:
        return {
            "request_id": request_id,
            "status": "Error: Not Found. No job with this ID was found.",
        }

    # If the job is complete and has an attachment, return it.
    if job.get("status") == "complete" and "attachment" in job:
        # Return a copy and remove the attachment from the store to save memory
        result = job.copy()
        # We no longer need to store the large file content in memory after it's been retrieved once.
        if "attachment" in export_jobs.get(request_id, {}):
            del export_jobs[request_id]["attachment"]
        return result

    return job


async def run_export_worker(
    request_id: str,
    table: str,
    query: Optional[str],
    fields: Optional[str],
    include_display_values: bool,
):
    """The background worker that performs the export and updates the job store."""
    exporter = ServiceNowExporter(request_id)
    try:
        output_dir = Path.home() / "Downloads"
        output_dir.mkdir(exist_ok=True)
        safe_table_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", table)
        output_file = output_dir / f"export_{safe_table_name}_{request_id}.csv"
        absolute_file_path = str(output_file.resolve())

        await exporter.fetch_and_write_data(
            table, absolute_file_path, query, fields, include_display_values
        )

        with open(output_file, "rb") as f:
            file_content = f.read()

        encoded_content = base64.b64encode(file_content).decode("utf-8")

        attachment = {
            "fileName": os.path.basename(output_file),
            "fileContent": encoded_content,
            "fileType": "text/csv",
        }

        # IMPROVEMENT: The progress message now includes the full file path.
        progress_message = (
            f"Export of {exporter.total_records} records complete! "
            f"File saved to your downloads folder at: {absolute_file_path}"
        )
        exporter.update_status(
            "complete", progress=progress_message, attachment=attachment
        )

    except Exception as e:
        log.error(
            f"Worker for '{request_id}' failed with an unexpected error: {e}",
            exc_info=True,
        )
        error_message = (
            f"Worker failed: An unexpected error occurred: {type(e).__name__}"
        )
        if export_jobs.get(request_id):
            export_jobs[request_id]["status"] = "failed"
            export_jobs[request_id]["error"] = error_message


if __name__ == "__main__":
    mcp.run(transport="stdio")
