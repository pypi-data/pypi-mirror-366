"""
Google Cloud MCP Server
Model Context Protocol server for Google Cloud Platform operations
"""

import os
import logging
import argparse
from typing import List, Dict, Any, Optional, Set
from mcp.server.fastmcp import FastMCP

from .big_query import BigQueryManager
from .cloud_storage import CloudStorageManager
from .cloud_logging import CloudLoggingManager
from .compute_engine import ComputeEngineManager

# Initialize MCP server
mcp = FastMCP("google-cloud-mcp")

# Global configuration
PROJECT_ID = None
SERVICE_ACCOUNT_PATH = None
ALLOWED_BUCKETS: Set[str] = set()
ALLOWED_DATASETS: Set[str] = set()
ALLOWED_LOG_BUCKETS: Set[str] = set()
ALLOWED_INSTANCES: Set[str] = set()

# Service managers
bigquery_manager = None
storage_manager = None
logging_manager = None
compute_manager = None

logger = logging.getLogger(__name__)

def setup_server(
    project_id: str,
    service_account_path: Optional[str] = None,
    allowed_buckets: str = "",
    allowed_datasets: str = "",
    allowed_log_buckets: str = "",
    allowed_instances: str = ""
):
    """Setup the MCP server with configuration"""
    global PROJECT_ID, SERVICE_ACCOUNT_PATH, ALLOWED_BUCKETS, ALLOWED_DATASETS
    global ALLOWED_LOG_BUCKETS, ALLOWED_INSTANCES
    global bigquery_manager, storage_manager, logging_manager, compute_manager
    
    PROJECT_ID = project_id
    SERVICE_ACCOUNT_PATH = service_account_path
    
    # Parse allowed resources (comma-separated)
    ALLOWED_BUCKETS = set(s.strip() for s in allowed_buckets.split(',') if s.strip()) if allowed_buckets else set()
    ALLOWED_DATASETS = set(s.strip() for s in allowed_datasets.split(',') if s.strip()) if allowed_datasets else set() 
    ALLOWED_LOG_BUCKETS = set(s.strip() for s in allowed_log_buckets.split(',') if s.strip()) if allowed_log_buckets else set()
    ALLOWED_INSTANCES = set(s.strip() for s in allowed_instances.split(',') if s.strip()) if allowed_instances else set()
    
    # Initialize service managers
    try:
        bigquery_manager = BigQueryManager(project_id, service_account_path)
        storage_manager = CloudStorageManager(project_id, service_account_path or "service-account-key.json")
        logging_manager = CloudLoggingManager(project_id, service_account_path)
        compute_manager = ComputeEngineManager(project_id, service_account_path)
        
        logger.info(f"Initialized Google Cloud MCP server for project: {project_id}")
        if ALLOWED_BUCKETS:
            logger.info(f"Allowed buckets: {ALLOWED_BUCKETS}")
        if ALLOWED_DATASETS:
            logger.info(f"Allowed datasets: {ALLOWED_DATASETS}")
        if ALLOWED_LOG_BUCKETS:
            logger.info(f"Allowed log buckets: {ALLOWED_LOG_BUCKETS}")
        if ALLOWED_INSTANCES:
            logger.info(f"Allowed instances: {ALLOWED_INSTANCES}")
            
    except Exception as e:
        logger.error(f"Failed to initialize service managers: {e}")
        raise

def validate_bucket_access(bucket_name: str) -> bool:
    """Validate if bucket access is allowed"""
    if not ALLOWED_BUCKETS:
        return True  # No restrictions if not configured
    return bucket_name in ALLOWED_BUCKETS

def validate_dataset_access(dataset_id: str) -> bool:
    """Validate if dataset access is allowed"""
    if not ALLOWED_DATASETS:
        return True  # No restrictions if not configured
    return dataset_id in ALLOWED_DATASETS

def validate_log_bucket_access(bucket_name: str) -> bool:
    """Validate if log bucket access is allowed"""
    if not ALLOWED_LOG_BUCKETS:
        return True  # No restrictions if not configured
    return bucket_name in ALLOWED_LOG_BUCKETS

def validate_instance_access(instance_name: str) -> bool:
    """Validate if instance access is allowed"""
    if not ALLOWED_INSTANCES:
        return True  # No restrictions if not configured
    return instance_name in ALLOWED_INSTANCES

# BigQuery Tools
@mcp.tool()
async def bigquery_run_query(query: str, dry_run: bool = False, max_results: int = 1000) -> str:
    """Execute a BigQuery SQL query
    
    Args:
        query: SQL query to execute
        dry_run: If True, only validate query without running it
        max_results: Maximum number of results to return (default: 1000)
    
    Returns:
        Query results or error message
    """
    try:
        result = bigquery_manager.run_query(
            query=query,
            dry_run=dry_run,
            max_results=max_results
        )
        
        if dry_run:
            bytes_processed = result.get('bytes_processed', 0)
            estimated_cost = result.get('estimated_cost_usd', 0)
            return f"Query validation successful.\nEstimated bytes processed: {bytes_processed}\nEstimated cost: ${estimated_cost:.4f} USD"
        
        rows = result.get('results', [])
        total_rows = result.get('total_rows', len(rows))
        bytes_processed = result.get('bytes_processed', 0)
        execution_time = result.get('execution_time_ms', 0)
        
        response = f"Query executed successfully.\n"
        response += f"Total rows: {total_rows}, Returned: {len(rows)}\n"
        response += f"Bytes processed: {bytes_processed}, Execution time: {execution_time}ms\n\n"
        
        if rows:
            response += "Sample results (first 5 rows):\n"
            for i, row in enumerate(rows[:5]):
                response += f"Row {i+1}: {row}\n"
            if len(rows) > 5:
                response += f"... and {len(rows) - 5} more rows"
        else:
            response += "No results returned."
        
        return response
        
    except Exception as e:
        return f"Error executing BigQuery query: {str(e)}"

@mcp.tool()
async def bigquery_list_datasets() -> str:
    """List all BigQuery datasets in the project
    
    Returns:
        List of datasets or error message
    """
    try:
        # Use the BigQuery client directly since manager doesn't have this method
        datasets = []
        for dataset_ref in bigquery_manager.client.list_datasets():
            # DatasetListItem only has dataset_id, project, and reference
            # For performance, we'll just show basic info and avoid extra API calls
            dataset_info = {
                'dataset_id': dataset_ref.dataset_id,
                'project': dataset_ref.project or PROJECT_ID,
                'full_name': f"{dataset_ref.project or PROJECT_ID}.{dataset_ref.dataset_id}"
            }
            
            if not ALLOWED_DATASETS or dataset_ref.dataset_id in ALLOWED_DATASETS:
                datasets.append(dataset_info)
        
        if not datasets:
            return "No datasets found or no access to allowed datasets"
        
        return f"Found {len(datasets)} datasets:\n" + "\n".join([f"- {ds['dataset_id']} (Project: {ds['project']})" for ds in datasets])
        
    except Exception as e:
        return f"Error listing BigQuery datasets: {str(e)}"

@mcp.tool()
async def bigquery_create_dataset(dataset_id: str, description: str = "", location: str = "US") -> str:
    """Create a new BigQuery dataset
    
    Args:
        dataset_id: ID for the new dataset
        description: Optional description for the dataset
        location: Dataset location (default: US)
    
    Returns:
        Success message or error
    """
    if not validate_dataset_access(dataset_id):
        return f"Access denied: Dataset '{dataset_id}' is not in allowed datasets list"
    
    try:
        from google.cloud import bigquery
        dataset = bigquery.Dataset(f"{PROJECT_ID}.{dataset_id}")
        dataset.location = location
        if description:
            dataset.description = description
        
        dataset = bigquery_manager.client.create_dataset(dataset)
        return f"Successfully created dataset '{dataset_id}' in location '{location}'"
        
    except Exception as e:
        return f"Error creating BigQuery dataset: {str(e)}"

@mcp.tool()
async def bigquery_get_dataset_info(dataset_id: str) -> str:
    """Get detailed information about a BigQuery dataset
    
    Args:
        dataset_id: ID of the dataset
    
    Returns:
        Dataset information or error message
    """
    if not validate_dataset_access(dataset_id):
        return f"Access denied: Dataset '{dataset_id}' is not in allowed datasets list"
    
    try:
        from google.cloud import bigquery
        dataset_ref = bigquery.DatasetReference(PROJECT_ID, dataset_id)
        dataset = bigquery_manager.client.get_dataset(dataset_ref)
        
        result = f"Dataset Information for '{dataset_id}':\n"
        result += f"Full Name: {dataset.full_dataset_id}\n"
        result += f"Location: {dataset.location or 'Unknown'}\n"
        result += f"Description: {dataset.description or 'No description'}\n"
        result += f"Created: {dataset.created.isoformat() if dataset.created else 'Unknown'}\n"
        result += f"Modified: {dataset.modified.isoformat() if dataset.modified else 'Unknown'}\n"
        result += f"Default Table Expiration: {dataset.default_table_expiration_ms or 'None'} ms\n"
        result += f"Labels: {dict(dataset.labels) if dataset.labels else 'None'}"
        
        return result
        
    except Exception as e:
        return f"Error getting dataset info for '{dataset_id}': {str(e)}"

@mcp.tool()
async def bigquery_load_csv_data(dataset_id: str, table_id: str, csv_file_path: str, skip_header: bool = True, write_mode: str = "WRITE_TRUNCATE") -> str:
    """Load data from CSV file to BigQuery table
    
    Args:
        dataset_id: Dataset ID
        table_id: Table ID
        csv_file_path: Path to CSV file
        skip_header: Whether to skip the first row (header)
        write_mode: Write mode (WRITE_TRUNCATE, WRITE_APPEND, WRITE_EMPTY)
    
    Returns:
        Success message or error
    """
    if not validate_dataset_access(dataset_id):
        return f"Access denied: Dataset '{dataset_id}' is not in allowed datasets list"
    
    try:
        result = bigquery_manager.load_data_from_csv(
            dataset_id=dataset_id,
            table_id=table_id,
            csv_path=csv_file_path,
            skip_leading_rows=1 if skip_header else 0,
            write_disposition=write_mode
        )
        return f"Successfully loaded CSV data from '{csv_file_path}' to table '{dataset_id}.{table_id}'"
        
    except Exception as e:
        return f"Error loading CSV data to BigQuery: {str(e)}"

@mcp.tool()
async def bigquery_export_table(dataset_id: str, table_id: str, destination_bucket: str, destination_path: str, file_format: str = "CSV") -> str:
    """Export BigQuery table to Cloud Storage
    
    Args:
        dataset_id: Dataset ID
        table_id: Table ID
        destination_bucket: Destination bucket name
        destination_path: Destination path in bucket
        file_format: Export format (CSV, JSON, AVRO)
    
    Returns:
        Success message or error
    """
    if not validate_dataset_access(dataset_id):
        return f"Access denied: Dataset '{dataset_id}' is not in allowed datasets list"
    if not validate_bucket_access(destination_bucket):
        return f"Access denied: Bucket '{destination_bucket}' is not in allowed buckets list"
    
    try:
        destination_uri = f"gs://{destination_bucket}/{destination_path}"
        
        if file_format.upper() == "CSV":
            result = bigquery_manager.export_table_to_csv(
                dataset_id=dataset_id,
                table_id=table_id,
                destination_uri=destination_uri
            )
        else:
            # For other formats, we'll fall back to a more generic approach
            return f"Export format '{file_format}' not yet supported. Currently only CSV is supported."
        
        return f"Successfully exported table '{dataset_id}.{table_id}' to '{destination_uri}'"
        
    except Exception as e:
        return f"Error exporting BigQuery table: {str(e)}"

@mcp.tool()
async def bigquery_list_jobs(max_results: int = 50, state_filter: str = "") -> str:
    """List BigQuery jobs
    
    Args:
        max_results: Maximum number of jobs to return
        state_filter: Filter by job state (RUNNING, DONE, PENDING)
    
    Returns:
        List of jobs or error message
    """
    try:
        jobs = bigquery_manager.list_jobs(max_results=max_results, state_filter=state_filter)
        
        if not jobs:
            return "No BigQuery jobs found"
            
        result = f"Found {len(jobs)} BigQuery jobs:\n"
        for job in jobs[:10]:
            result += f"- {job.get('job_id', 'Unknown')}: {job.get('state', 'Unknown')} ({job.get('job_type', 'Unknown')})\n"
            result += f"  Created: {job.get('creation_time', 'Unknown')}\n"
            if job.get('error_result'):
                result += f"  Error: {job.get('error_result', 'None')}\n"
        
        if len(jobs) > 10:
            result += f"... and {len(jobs) - 10} more jobs"
            
        return result
        
    except Exception as e:
        return f"Error listing BigQuery jobs: {str(e)}"

@mcp.tool()
async def bigquery_cancel_job(job_id: str) -> str:
    """Cancel a BigQuery job
    
    Args:
        job_id: ID of the job to cancel
    
    Returns:
        Success message or error
    """
    try:
        success = bigquery_manager.cancel_job(job_id)
        if success:
            return f"Successfully cancelled BigQuery job '{job_id}'"
        else:
            return f"Could not cancel BigQuery job '{job_id}' (may already be completed)"
        
    except Exception as e:
        return f"Error cancelling BigQuery job '{job_id}': {str(e)}"

# Cloud Storage Tools
@mcp.tool()
async def storage_list_buckets() -> str:
    """List all Cloud Storage buckets
    
    Returns:
        List of buckets or error message
    """
    try:
        buckets = storage_manager.list_buckets()
        
        if ALLOWED_BUCKETS:
            # Filter buckets based on allowed list
            buckets = [b for b in buckets if b.get('name') in ALLOWED_BUCKETS]
        
        return f"Found {len(buckets)} buckets:\n" + "\n".join([f"- {b['name']}: {b.get('location', 'Unknown location')}" for b in buckets])
        
    except Exception as e:
        return f"Error listing Cloud Storage buckets: {str(e)}"

@mcp.tool()
async def storage_create_bucket(bucket_name: str, location: str = "US") -> str:
    """Create a new Cloud Storage bucket
    
    Args:
        bucket_name: Name for the new bucket
        location: Location for the bucket (default: US)
    
    Returns:
        Success message or error
    """
    if not validate_bucket_access(bucket_name):
        return f"Access denied: Bucket '{bucket_name}' is not in allowed buckets list"
    
    try:
        result = storage_manager.create_bucket(bucket_name, location)
        return f"Successfully created bucket '{bucket_name}' in location '{location}'"
        
    except Exception as e:
        return f"Error creating Cloud Storage bucket: {str(e)}"

@mcp.tool()
async def storage_list_objects(bucket_name: str, prefix: str = "") -> str:
    """List objects in a Cloud Storage bucket
    
    Args:
        bucket_name: Name of the bucket
        prefix: Optional prefix to filter objects
    
    Returns:
        List of objects or error message
    """
    if not validate_bucket_access(bucket_name):
        return f"Access denied: Bucket '{bucket_name}' is not in allowed buckets list"
    
    try:
        objects = storage_manager.list_objects(bucket_name, prefix)
        return f"Found {len(objects)} objects in bucket '{bucket_name}':\n" + "\n".join([f"- {obj['name']}: {obj.get('size', 0)} bytes" for obj in objects[:20]]) + ("..." if len(objects) > 20 else "")
        
    except Exception as e:
        return f"Error listing objects in bucket '{bucket_name}': {str(e)}"

@mcp.tool()
async def storage_upload_file(bucket_name: str, source_file_path: str, destination_blob_name: str) -> str:
    """Upload a file to Cloud Storage bucket
    
    Args:
        bucket_name: Name of the bucket
        source_file_path: Local path to the file to upload
        destination_blob_name: Name for the blob in the bucket
    
    Returns:
        Success message or error
    """
    if not validate_bucket_access(bucket_name):
        return f"Access denied: Bucket '{bucket_name}' is not in allowed buckets list"
    
    try:
        result = storage_manager.upload_file(bucket_name, source_file_path, destination_blob_name)
        return f"Successfully uploaded '{source_file_path}' to '{bucket_name}/{destination_blob_name}'"
        
    except Exception as e:
        return f"Error uploading file to bucket '{bucket_name}': {str(e)}"

@mcp.tool()
async def storage_download_file(bucket_name: str, source_blob_name: str, destination_file_path: str) -> str:
    """Download a file from Cloud Storage bucket
    
    Args:
        bucket_name: Name of the bucket
        source_blob_name: Name of the blob in the bucket
        destination_file_path: Local path where to save the file
    
    Returns:
        Success message or error
    """
    if not validate_bucket_access(bucket_name):
        return f"Access denied: Bucket '{bucket_name}' is not in allowed buckets list"
    
    try:
        result = storage_manager.download_file(bucket_name, source_blob_name, destination_file_path)
        return f"Successfully downloaded '{bucket_name}/{source_blob_name}' to '{destination_file_path}'"
        
    except Exception as e:
        return f"Error downloading file from bucket '{bucket_name}': {str(e)}"

@mcp.tool()
async def storage_delete_object(bucket_name: str, blob_name: str) -> str:
    """Delete an object from Cloud Storage bucket
    
    Args:
        bucket_name: Name of the bucket
        blob_name: Name of the blob to delete
    
    Returns:
        Success message or error
    """
    if not validate_bucket_access(bucket_name):
        return f"Access denied: Bucket '{bucket_name}' is not in allowed buckets list"
    
    try:
        result = storage_manager.delete_object(bucket_name, blob_name)
        if result:
            return f"Successfully deleted '{blob_name}' from bucket '{bucket_name}'"
        else:
            return f"Object '{blob_name}' not found in bucket '{bucket_name}'"
        
    except Exception as e:
        return f"Error deleting object from bucket '{bucket_name}': {str(e)}"

@mcp.tool()
async def storage_get_bucket_info(bucket_name: str) -> str:
    """Get detailed information about a Cloud Storage bucket
    
    Args:
        bucket_name: Name of the bucket
    
    Returns:
        Bucket information or error message
    """
    if not validate_bucket_access(bucket_name):
        return f"Access denied: Bucket '{bucket_name}' is not in allowed buckets list"
    
    try:
        info = storage_manager.get_bucket_info(bucket_name)
        result = f"Bucket Information for '{bucket_name}':\n"
        result += f"Location: {info.get('location', 'Unknown')}\n"
        result += f"Storage Class: {info.get('storage_class', 'Unknown')}\n" 
        result += f"Created: {info.get('created', 'Unknown')}\n"
        result += f"Versioning: {'Enabled' if info.get('versioning_enabled') else 'Disabled'}\n"
        result += f"Labels: {info.get('labels', {})}\n"
        result += f"Lifecycle Rules: {info.get('lifecycle_rules', 0)}"
        return result
        
    except Exception as e:
        return f"Error getting bucket info for '{bucket_name}': {str(e)}"

@mcp.tool()
async def storage_generate_signed_url(bucket_name: str, blob_name: str, expiration_minutes: int = 60, method: str = "GET") -> str:
    """Generate a signed URL for temporary access to a Cloud Storage object
    
    Args:
        bucket_name: Name of the bucket
        blob_name: Name of the blob
        expiration_minutes: URL expiration time in minutes (default: 60)
        method: HTTP method (GET, PUT, POST, DELETE)
    
    Returns:
        Signed URL or error message
    """
    if not validate_bucket_access(bucket_name):
        return f"Access denied: Bucket '{bucket_name}' is not in allowed buckets list"
    
    try:
        url = storage_manager.generate_signed_url(bucket_name, blob_name, expiration_minutes, method)
        return f"Signed URL for '{bucket_name}/{blob_name}' (expires in {expiration_minutes} minutes):\n{url}"
        
    except Exception as e:
        return f"Error generating signed URL for '{bucket_name}/{blob_name}': {str(e)}"

@mcp.tool()
async def storage_copy_object(source_bucket: str, source_blob: str, dest_bucket: str, dest_blob: str) -> str:
    """Copy an object between Cloud Storage buckets
    
    Args:
        source_bucket: Source bucket name
        source_blob: Source blob name
        dest_bucket: Destination bucket name  
        dest_blob: Destination blob name
    
    Returns:
        Success message or error
    """
    if not validate_bucket_access(source_bucket):
        return f"Access denied: Source bucket '{source_bucket}' is not in allowed buckets list"
    if not validate_bucket_access(dest_bucket):
        return f"Access denied: Destination bucket '{dest_bucket}' is not in allowed buckets list"
    
    try:
        result = storage_manager.copy_object(source_bucket, source_blob, dest_bucket, dest_blob)
        return f"Successfully copied '{source_bucket}/{source_blob}' to '{dest_bucket}/{dest_blob}'"
        
    except Exception as e:
        return f"Error copying object: {str(e)}"

@mcp.tool()
async def storage_move_object(source_bucket: str, source_blob: str, dest_bucket: str, dest_blob: str) -> str:
    """Move an object between Cloud Storage buckets
    
    Args:
        source_bucket: Source bucket name
        source_blob: Source blob name
        dest_bucket: Destination bucket name
        dest_blob: Destination blob name
    
    Returns:
        Success message or error
    """
    if not validate_bucket_access(source_bucket):
        return f"Access denied: Source bucket '{source_bucket}' is not in allowed buckets list"
    if not validate_bucket_access(dest_bucket):
        return f"Access denied: Destination bucket '{dest_bucket}' is not in allowed buckets list"
    
    try:
        result = storage_manager.move_object(source_bucket, source_blob, dest_bucket, dest_blob)
        return f"Successfully moved '{source_bucket}/{source_blob}' to '{dest_bucket}/{dest_blob}'"
        
    except Exception as e:
        return f"Error moving object: {str(e)}"

@mcp.tool()
async def storage_enable_versioning(bucket_name: str, enabled: bool = True) -> str:
    """Enable or disable versioning for a Cloud Storage bucket
    
    Args:
        bucket_name: Name of the bucket
        enabled: Whether to enable (True) or disable (False) versioning
    
    Returns:
        Success message or error
    """
    if not validate_bucket_access(bucket_name):
        return f"Access denied: Bucket '{bucket_name}' is not in allowed buckets list"
    
    try:
        result = storage_manager.enable_versioning(bucket_name, enabled)
        status = "enabled" if enabled else "disabled"
        return f"Successfully {status} versioning for bucket '{bucket_name}'"
        
    except Exception as e:
        return f"Error updating versioning for bucket '{bucket_name}': {str(e)}"

@mcp.tool()
async def storage_get_bucket_size(bucket_name: str) -> str:
    """Get size statistics for a Cloud Storage bucket
    
    Args:
        bucket_name: Name of the bucket
    
    Returns:
        Bucket size information or error message
    """
    if not validate_bucket_access(bucket_name):
        return f"Access denied: Bucket '{bucket_name}' is not in allowed buckets list"
    
    try:
        info = storage_manager.get_bucket_size(bucket_name)
        result = f"Bucket Size Statistics for '{bucket_name}':\n"
        result += f"Total Objects: {info.get('total_objects', 0)}\n"
        result += f"Total Size: {info.get('total_size_bytes', 0)} bytes\n"
        result += f"Size (MB): {info.get('total_size_bytes', 0) / (1024*1024):.2f} MB\n"
        result += f"Size (GB): {info.get('total_size_bytes', 0) / (1024*1024*1024):.2f} GB"
        return result
        
    except Exception as e:
        return f"Error getting bucket size for '{bucket_name}': {str(e)}"

@mcp.tool()
async def storage_set_bucket_lifecycle(bucket_name: str, age_days: int = 30, action: str = "Delete") -> str:
    """Set lifecycle rules for a Cloud Storage bucket
    
    Args:
        bucket_name: Name of the bucket
        age_days: Age in days after which to apply the action
        action: Action to take (Delete, SetStorageClass)
    
    Returns:
        Success message or error
    """
    if not validate_bucket_access(bucket_name):
        return f"Access denied: Bucket '{bucket_name}' is not in allowed buckets list"
    
    try:
        # Call storage manager method with correct parameters
        result = storage_manager.set_bucket_lifecycle(
            bucket_name=bucket_name,
            age_days=age_days,
            action=action
        )
        return f"Successfully set lifecycle rule for bucket '{bucket_name}': {action} objects after {age_days} days"
        
    except Exception as e:
        return f"Error setting lifecycle rules for bucket '{bucket_name}': {str(e)}"

# Cloud Logging Tools
@mcp.tool()
async def logging_write_log(log_name: str, message: str, severity: str = "INFO") -> str:
    """Write a log entry to Cloud Logging
    
    Args:
        log_name: Name of the log
        message: Log message
        severity: Log severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Success message or error
    """
    if not validate_log_bucket_access(log_name):
        return f"Access denied: Log '{log_name}' is not in allowed log buckets list"
    
    try:
        result = logging_manager.write_log(log_name, message, severity)
        return f"Successfully wrote log entry to '{log_name}' with severity '{severity}'"
        
    except Exception as e:
        return f"Error writing log: {str(e)}"

@mcp.tool()
async def logging_read_logs(log_filter: str = "", max_entries: int = 50) -> str:
    """Read recent log entries from Cloud Logging
    
    Args:
        log_filter: Optional filter for log entries
        max_entries: Maximum number of entries to return (default: 50)
    
    Returns:
        Log entries or error message
    """
    try:
        entries = logging_manager.read_logs(log_filter, max_results=max_entries)
        
        # Filter entries based on allowed log buckets if configured
        if ALLOWED_LOG_BUCKETS:
            filtered_entries = []
            for entry in entries:
                log_name = entry.get('log_name', '')
                # Extract log name from full path (projects/PROJECT/logs/LOG_NAME)
                if '/logs/' in log_name:
                    simple_log_name = log_name.split('/logs/')[-1]
                else:
                    simple_log_name = log_name
                    
                if simple_log_name in ALLOWED_LOG_BUCKETS:
                    filtered_entries.append(entry)
            entries = filtered_entries
        
        if not entries:
            return "No log entries found matching the filter criteria"
            
        result = f"Found {len(entries)} log entries:\n"
        for i, entry in enumerate(entries[:10]):
            timestamp = entry.get('timestamp', 'Unknown')
            severity = entry.get('severity', 'INFO')
            text_msg = entry.get('text_payload')
            json_msg = entry.get('json_payload')
            message = text_msg or str(json_msg) if json_msg else 'No message'
            result += f"[{timestamp}] {severity}: {message}\n"
        
        if len(entries) > 10:
            result += f"... and {len(entries) - 10} more entries"
            
        return result
        
    except Exception as e:
        return f"Error reading logs: {str(e)}"

@mcp.tool()
async def logging_list_logs() -> str:
    """List all log names in the project
    
    Returns:
        List of log names or error message
    """
    try:
        logs = logging_manager.list_logs()
        
        # Filter logs based on allowed log buckets if configured
        if ALLOWED_LOG_BUCKETS:
            filtered_logs = [log for log in logs if any(allowed in log for allowed in ALLOWED_LOG_BUCKETS)]
            logs = filtered_logs
        
        if not logs:
            return "No logs found"
            
        return f"Found {len(logs)} logs:\n" + "\n".join([f"- {log}" for log in logs[:20]]) + ("..." if len(logs) > 20 else "")
        
    except Exception as e:
        return f"Error listing logs: {str(e)}"

@mcp.tool()
async def logging_delete_log(log_name: str) -> str:
    """Delete a log
    
    Args:
        log_name: Name of the log to delete
    
    Returns:
        Success message or error
    """
    if not validate_log_bucket_access(log_name):
        return f"Access denied: Log '{log_name}' is not in allowed log buckets list"
    
    try:
        success = logging_manager.delete_log(log_name)
        if success:
            return f"Successfully deleted log '{log_name}'"
        else:
            return f"Log '{log_name}' not found or could not be deleted"
        
    except Exception as e:
        return f"Error deleting log '{log_name}': {str(e)}"

@mcp.tool()
async def logging_create_log_sink(sink_name: str, destination: str, log_filter: str = "") -> str:
    """Create a log sink to export logs to another service
    
    Args:
        sink_name: Name for the sink
        destination: Destination (e.g., bigquery://project.dataset, storage://bucket-name)
        log_filter: Optional filter for which logs to export
    
    Returns:
        Success message or error
    """
    try:
        result = logging_manager.create_log_sink(
            sink_name=sink_name,
            destination=destination,
            filter_string=log_filter if log_filter else None
        )
        return f"Successfully created log sink '{sink_name}' to destination '{destination}'"
        
    except Exception as e:
        return f"Error creating log sink '{sink_name}': {str(e)}"

@mcp.tool()
async def logging_list_log_sinks() -> str:
    """List all log sinks in the project
    
    Returns:
        List of log sinks or error message
    """
    try:
        sinks = logging_manager.list_log_sinks()
        
        if not sinks:
            return "No log sinks found"
            
        result = f"Found {len(sinks)} log sinks:\n"
        for sink in sinks:
            result += f"- {sink.get('name', 'Unknown')}\n"
            result += f"  Destination: {sink.get('destination', 'Unknown')}\n"
            result += f"  Filter: {sink.get('filter', 'None')}\n"
            
        return result
        
    except Exception as e:
        return f"Error listing log sinks: {str(e)}"

@mcp.tool()
async def logging_delete_log_sink(sink_name: str) -> str:
    """Delete a log sink
    
    Args:
        sink_name: Name of the sink to delete
    
    Returns:
        Success message or error
    """
    try:
        success = logging_manager.delete_log_sink(sink_name)
        if success:
            return f"Successfully deleted log sink '{sink_name}'"
        else:
            return f"Log sink '{sink_name}' not found or could not be deleted"
        
    except Exception as e:
        return f"Error deleting log sink '{sink_name}': {str(e)}"

@mcp.tool()
async def logging_export_logs_to_bigquery(dataset_id: str, table_id: str, log_filter: str = "", days_back: int = 1) -> str:
    """Export logs to BigQuery
    
    Args:
        dataset_id: BigQuery dataset ID
        table_id: BigQuery table ID
        log_filter: Filter for which logs to export
        days_back: Number of days back to export (default: 1)
    
    Returns:
        Success message or error
    """
    if not validate_dataset_access(dataset_id):
        return f"Access denied: Dataset '{dataset_id}' is not in allowed datasets list"
    
    try:
        result = logging_manager.export_logs_to_bigquery(
            dataset_id=dataset_id,
            table_id=table_id,
            filter_=log_filter,
            days_back=days_back
        )
        return f"Successfully exported logs to BigQuery table '{dataset_id}.{table_id}'"
        
    except Exception as e:
        return f"Error exporting logs to BigQuery: {str(e)}"

@mcp.tool()
async def logging_create_log_bucket(bucket_id: str, location: str = "global", retention_days: int = 30) -> str:
    """Create a log bucket for storing logs
    
    Args:
        bucket_id: ID for the log bucket
        location: Location for the bucket (default: global)
        retention_days: Log retention period in days (default: 30)
    
    Returns:
        Success message or error
    """
    if not validate_log_bucket_access(bucket_id):
        return f"Access denied: Log bucket '{bucket_id}' is not in allowed log buckets list"
    
    try:
        result = logging_manager.create_log_bucket(
            bucket_id=bucket_id,
            retention_days=retention_days
        )
        return f"Successfully created log bucket '{bucket_id}' with {retention_days} days retention"
        
    except Exception as e:
        return f"Error creating log bucket '{bucket_id}': {str(e)}"

# Compute Engine Tools
@mcp.tool()
async def compute_list_instances(zone: str = "") -> str:
    """List Compute Engine instances
    
    Args:
        zone: Optional zone filter, if empty lists from all zones
    
    Returns:
        List of instances or error message
    """
    try:
        instances = compute_manager.list_instances(zone if zone else None)
        
        if ALLOWED_INSTANCES:
            # Filter instances based on allowed list
            instances = [inst for inst in instances if inst.get('name') in ALLOWED_INSTANCES]
        
        return f"Found {len(instances)} instances:\n" + "\n".join([f"- {inst['name']}: {inst.get('status', 'Unknown')} in {inst.get('zone', 'Unknown zone')}" for inst in instances])
        
    except Exception as e:
        return f"Error listing Compute Engine instances: {str(e)}"

@mcp.tool()
async def compute_create_instance(instance_name: str, zone: str, machine_type: str = "e2-micro") -> str:
    """Create a new Compute Engine instance
    
    Args:
        instance_name: Name for the new instance
        zone: Zone where to create the instance
        machine_type: Machine type (default: e2-micro)
    
    Returns:
        Success message or error
    """
    if not validate_instance_access(instance_name):
        return f"Access denied: Instance '{instance_name}' is not in allowed instances list"
    
    try:
        result = compute_manager.create_instance(instance_name, zone, machine_type)
        return f"Successfully initiated creation of instance '{instance_name}' in zone '{zone}'"
        
    except Exception as e:
        return f"Error creating Compute Engine instance: {str(e)}"

@mcp.tool()
async def compute_delete_instance(instance_name: str, zone: str) -> str:
    """Delete a Compute Engine instance
    
    Args:
        instance_name: Name of the instance to delete
        zone: Zone where the instance is located
    
    Returns:
        Success message or error
    """
    if not validate_instance_access(instance_name):
        return f"Access denied: Instance '{instance_name}' is not in allowed instances list"
    
    try:
        result = compute_manager.delete_instance(instance_name, zone)
        return f"Successfully initiated deletion of instance '{instance_name}' in zone '{zone}'"
        
    except Exception as e:
        return f"Error deleting Compute Engine instance: {str(e)}"

@mcp.tool()
async def compute_start_instance(instance_name: str, zone: str) -> str:
    """Start a Compute Engine instance
    
    Args:
        instance_name: Name of the instance to start
        zone: Zone where the instance is located
    
    Returns:
        Success message or error
    """
    if not validate_instance_access(instance_name):
        return f"Access denied: Instance '{instance_name}' is not in allowed instances list"
    
    try:
        result = compute_manager.start_instance(instance_name, zone)
        return f"Successfully initiated start of instance '{instance_name}' in zone '{zone}'"
        
    except Exception as e:
        return f"Error starting Compute Engine instance: {str(e)}"

@mcp.tool()
async def compute_stop_instance(instance_name: str, zone: str) -> str:
    """Stop a Compute Engine instance
    
    Args:
        instance_name: Name of the instance to stop
        zone: Zone where the instance is located
    
    Returns:
        Success message or error
    """
    if not validate_instance_access(instance_name):
        return f"Access denied: Instance '{instance_name}' is not in allowed instances list"
    
    try:
        result = compute_manager.stop_instance(instance_name, zone)
        return f"Successfully initiated stop of instance '{instance_name}' in zone '{zone}'"
        
    except Exception as e:
        return f"Error stopping Compute Engine instance: {str(e)}"

@mcp.tool()
async def compute_restart_instance(instance_name: str, zone: str) -> str:
    """Restart a Compute Engine instance
    
    Args:
        instance_name: Name of the instance to restart
        zone: Zone where the instance is located
    
    Returns:
        Success message or error
    """
    if not validate_instance_access(instance_name):
        return f"Access denied: Instance '{instance_name}' is not in allowed instances list"
    
    try:
        # First check instance status
        try:
            instance_info = compute_manager.get_instance(instance_name, zone)
            current_status = instance_info.get('status', 'UNKNOWN')
            
            if current_status not in ['RUNNING', 'STOPPING']:
                return f"Cannot restart instance '{instance_name}': current status is '{current_status}'. Instance must be RUNNING or STOPPING to restart."
        except Exception:
            # If we can't get status, proceed anyway
            pass
        
        result = compute_manager.restart_instance(instance_name, zone)
        return f"Successfully initiated restart of instance '{instance_name}' in zone '{zone}'"
        
    except Exception as e:
        error_msg = str(e)
        if "Invalid value for field" in error_msg and "RUNNING" in error_msg:
            return f"Cannot restart instance '{instance_name}': instance is not in a RUNNING state. Only running instances can be restarted."
        return f"Error restarting Compute Engine instance: {error_msg}"

@mcp.tool()
async def compute_get_instance(instance_name: str, zone: str) -> str:
    """Get detailed information about a Compute Engine instance
    
    Args:
        instance_name: Name of the instance
        zone: Zone where the instance is located
    
    Returns:
        Instance information or error message
    """
    if not validate_instance_access(instance_name):
        return f"Access denied: Instance '{instance_name}' is not in allowed instances list"
    
    try:
        info = compute_manager.get_instance(instance_name, zone)
        result = f"Instance Information for '{instance_name}':\n"
        result += f"Status: {info.get('status', 'Unknown')}\n"
        result += f"Zone: {info.get('zone', 'Unknown')}\n"
        result += f"Machine Type: {info.get('machine_type', 'Unknown')}\n"
        result += f"Created: {info.get('creation_timestamp', 'Unknown')}\n"
        result += f"Internal IP: {info.get('internal_ip', 'None')}\n"
        result += f"External IP: {info.get('external_ip', 'None')}\n"
        result += f"Boot Disk: {info.get('boot_disk_size_gb', 'Unknown')} GB\n"
        result += f"Network Tags: {info.get('tags', [])}\n"
        result += f"Labels: {info.get('labels', {})}"
        return result
        
    except Exception as e:
        return f"Error getting instance info for '{instance_name}': {str(e)}"

@mcp.tool()
async def compute_list_zones() -> str:
    """List all available Compute Engine zones
    
    Returns:
        List of zones or error message
    """
    try:
        zones = compute_manager.list_zones()
        return f"Found {len(zones)} available zones:\n" + "\n".join([f"- {zone}" for zone in zones[:20]]) + ("..." if len(zones) > 20 else "")
        
    except Exception as e:
        return f"Error listing Compute Engine zones: {str(e)}"

@mcp.tool()
async def compute_wait_for_operation(operation_name: str, zone: str, timeout_minutes: int = 5) -> str:
    """Wait for a Compute Engine operation to complete
    
    Args:
        operation_name: Name of the operation to wait for
        zone: Zone where the operation is running
        timeout_minutes: Maximum time to wait in minutes (default: 5)
    
    Returns:
        Operation status or timeout message
    """
    try:
        timeout_seconds = timeout_minutes * 60
        success = compute_manager.wait_for_operation(operation_name, zone, timeout_seconds)
        if success:
            return f"Operation '{operation_name}' completed successfully"
        else:
            return f"Operation '{operation_name}' timed out after {timeout_minutes} minutes"
        
    except Exception as e:
        return f"Error waiting for operation '{operation_name}': {str(e)}"

def main():
    """Main function to run the MCP server"""
    parser = argparse.ArgumentParser(description='Google Cloud MCP Server')
    parser.add_argument('--project-id', type=str, required=True,
                        help='Google Cloud Project ID')
    parser.add_argument('--service-account-path', type=str, default=None,
                        help='Path to service account JSON file')
    parser.add_argument('--allowed-buckets', type=str, default="",
                        help='Comma-separated list of allowed storage buckets')
    parser.add_argument('--allowed-datasets', type=str, default="",
                        help='Comma-separated list of allowed BigQuery datasets')
    parser.add_argument('--allowed-log-buckets', type=str, default="",
                        help='Comma-separated list of allowed log buckets')
    parser.add_argument('--allowed-instances', type=str, default="",
                        help='Comma-separated list of allowed compute instances')
    
    args = parser.parse_args()
    
    # Setup server with configuration
    setup_server(
        project_id=args.project_id,
        service_account_path=args.service_account_path,
        allowed_buckets=args.allowed_buckets,
        allowed_datasets=args.allowed_datasets,
        allowed_log_buckets=args.allowed_log_buckets,
        allowed_instances=args.allowed_instances
    )
    
    # Run the server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()