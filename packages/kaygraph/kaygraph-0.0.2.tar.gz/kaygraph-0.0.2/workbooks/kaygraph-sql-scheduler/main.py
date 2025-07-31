#!/usr/bin/env python3
"""
Main entry point for scheduled SQL jobs using KayGraph.
Designed to be called from cron or other schedulers.

Usage:
    python main.py --job=daily_sales_etl
    python main.py --job=hourly_metrics --date=2024-01-15
"""

import argparse
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sql_nodes import SQLNode
from etl_pipeline import create_etl_pipeline
from monitoring import setup_monitoring, send_alert, log_execution_metrics


# Job registry - maps job names to their configurations
JOBS = {
    "daily_sales_etl": {
        "description": "Daily sales ETL pipeline",
        "pipeline": "sales_etl",
        "default_params": {
            "retention_days": 365
        }
    },
    "hourly_metrics": {
        "description": "Hourly metrics aggregation",
        "pipeline": "metrics_aggregation",
        "default_params": {
            "metrics_window_hours": 24
        }
    },
    "weekly_customer_summary": {
        "description": "Weekly customer behavior summary",
        "pipeline": "customer_summary",
        "default_params": {
            "week_offset": 1
        }
    }
}


def get_db_config():
    """Get database configuration from environment variables."""
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "5432")),
        "database": os.environ.get("DB_NAME", "analytics"),
        "user": os.environ.get("DB_USER", "etl_user"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "sslmode": os.environ.get("DB_SSLMODE", "prefer")
    }


def create_pipeline(pipeline_name: str):
    """Create pipeline based on name."""
    if pipeline_name == "sales_etl":
        return create_etl_pipeline()
    elif pipeline_name == "metrics_aggregation":
        # Import and create other pipelines
        from metrics_pipeline import create_metrics_pipeline
        return create_metrics_pipeline()
    elif pipeline_name == "customer_summary":
        from customer_pipeline import create_customer_pipeline
        return create_customer_pipeline()
    else:
        raise ValueError(f"Unknown pipeline: {pipeline_name}")


def run_job(job_name: str, override_params: dict = None):
    """Run a specific job with error handling and monitoring."""
    if job_name not in JOBS:
        raise ValueError(f"Unknown job: {job_name}. Available jobs: {list(JOBS.keys())}")
    
    job_config = JOBS[job_name]
    start_time = datetime.utcnow()
    
    # Setup logging for this job
    logger = logging.getLogger(job_name)
    logger.info(f"Starting job: {job_name}")
    logger.info(f"Description: {job_config['description']}")
    
    try:
        # Configure database connection pool
        db_config = get_db_config()
        SQLNode.configure_pool(db_config, pool_size=10)
        logger.info("Database connection pool configured")
        
        # Create pipeline
        pipeline = create_pipeline(job_config["pipeline"])
        
        # Prepare shared context
        shared = {
            "job_name": job_name,
            "job_start_time": start_time,
            **job_config["default_params"]
        }
        
        # Apply parameter overrides
        if override_params:
            shared.update(override_params)
            logger.info(f"Applied parameter overrides: {override_params}")
        
        # Run the pipeline
        logger.info("Executing pipeline...")
        with pipeline:  # Use context manager for resource cleanup
            final_action = pipeline.run(shared)
        
        # Check results
        if shared.get("etl_status") == "validation_failed":
            raise Exception("Pipeline validation failed")
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Log success metrics
        metrics = {
            "job_name": job_name,
            "status": "success",
            "execution_time": execution_time,
            "rows_processed": shared.get("extraction_stats", {}).get("row_count", 0),
            "end_time": datetime.utcnow()
        }
        
        log_execution_metrics(metrics)
        logger.info(f"Job completed successfully in {execution_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        # Handle errors
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.error(f"Job failed: {str(e)}", exc_info=True)
        
        # Log failure metrics
        metrics = {
            "job_name": job_name,
            "status": "failed",
            "execution_time": execution_time,
            "error": str(e),
            "end_time": datetime.utcnow()
        }
        
        log_execution_metrics(metrics)
        
        # Send alert
        send_alert(
            subject=f"ETL Job Failed: {job_name}",
            message=f"Job {job_name} failed after {execution_time:.2f} seconds.\nError: {str(e)}",
            severity="high"
        )
        
        return False


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats."""
    formats = [
        "%Y-%m-%d",
        "%Y%m%d",
        "%Y-%m-%d %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def main():
    """Main entry point for scheduled execution."""
    parser = argparse.ArgumentParser(
        description="KayGraph SQL Scheduler - Run ETL jobs"
    )
    
    parser.add_argument(
        "--job",
        required=True,
        choices=list(JOBS.keys()),
        help="Job to execute"
    )
    
    parser.add_argument(
        "--date",
        help="Override date for the job (YYYY-MM-DD format)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without running"
    )
    
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f"/var/log/kaygraph/{args.job}.log", mode='a')
        ]
    )
    
    # Setup monitoring
    setup_monitoring()
    
    # Prepare override parameters
    override_params = {}
    if args.date:
        date = parse_date(args.date)
        override_params["end_date"] = date.date()
        override_params["start_date"] = (date - timedelta(days=1)).date()
    
    if args.dry_run:
        logger = logging.getLogger("main")
        logger.info(f"DRY RUN: Would execute job '{args.job}'")
        logger.info(f"Job config: {JOBS[args.job]}")
        logger.info(f"Override params: {override_params}")
        return 0
    
    # Run the job
    success = run_job(args.job, override_params)
    
    # Exit with appropriate code for scheduler
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())