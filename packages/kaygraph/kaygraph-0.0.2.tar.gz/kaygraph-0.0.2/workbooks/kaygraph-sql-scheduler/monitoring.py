"""
Monitoring and alerting utilities for SQL scheduler.
Integrates with various monitoring systems.
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


# Global monitoring configuration
MONITORING_CONFIG = {
    "metrics_file": "/var/log/kaygraph/metrics.jsonl",
    "alert_webhook": os.environ.get("ALERT_WEBHOOK_URL"),
    "email_config": {
        "smtp_host": os.environ.get("SMTP_HOST", "localhost"),
        "smtp_port": int(os.environ.get("SMTP_PORT", "25")),
        "from_email": os.environ.get("ALERT_FROM_EMAIL", "etl@example.com"),
        "to_emails": os.environ.get("ALERT_TO_EMAILS", "ops@example.com").split(",")
    },
    "slack_webhook": os.environ.get("SLACK_WEBHOOK_URL"),
    "pagerduty_key": os.environ.get("PAGERDUTY_INTEGRATION_KEY")
}


def setup_monitoring():
    """Initialize monitoring systems."""
    # Ensure metrics directory exists
    metrics_dir = os.path.dirname(MONITORING_CONFIG["metrics_file"])
    os.makedirs(metrics_dir, exist_ok=True)
    
    logger.info("Monitoring system initialized")


def log_execution_metrics(metrics: Dict[str, Any]):
    """Log execution metrics to metrics file and monitoring systems."""
    # Add timestamp if not present
    if "timestamp" not in metrics:
        metrics["timestamp"] = datetime.utcnow().isoformat()
    
    # Write to metrics file (JSONL format for easy parsing)
    try:
        with open(MONITORING_CONFIG["metrics_file"], "a") as f:
            f.write(json.dumps(metrics) + "\n")
    except Exception as e:
        logger.error(f"Failed to write metrics: {e}")
    
    # Send to monitoring systems
    send_to_prometheus(metrics)
    send_to_datadog(metrics)
    
    # Log summary
    logger.info(f"Metrics logged: job={metrics.get('job_name')}, "
               f"status={metrics.get('status')}, "
               f"execution_time={metrics.get('execution_time', 0):.2f}s")


def send_alert(subject: str, message: str, severity: str = "medium", 
               metadata: Optional[Dict[str, Any]] = None):
    """Send alerts through configured channels."""
    alert_data = {
        "subject": subject,
        "message": message,
        "severity": severity,
        "timestamp": datetime.utcnow().isoformat(),
        "hostname": os.uname().nodename,
        "metadata": metadata or {}
    }
    
    # Send through different channels based on severity
    if severity in ["high", "critical"]:
        send_pagerduty_alert(alert_data)
        send_slack_alert(alert_data, urgent=True)
        send_email_alert(alert_data)
    else:
        send_slack_alert(alert_data, urgent=False)
        if severity == "medium":
            send_email_alert(alert_data)
    
    # Log the alert
    logger.warning(f"Alert sent: {subject} (severity: {severity})")


def send_to_prometheus(metrics: Dict[str, Any]):
    """Send metrics to Prometheus pushgateway."""
    # This would push to Prometheus in production
    # Example using prometheus_client library:
    """
    from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
    
    registry = CollectorRegistry()
    
    # Job execution time
    execution_time = Gauge('etl_job_execution_time_seconds', 
                          'ETL job execution time',
                          ['job_name', 'status'], 
                          registry=registry)
    
    execution_time.labels(
        job_name=metrics['job_name'],
        status=metrics['status']
    ).set(metrics.get('execution_time', 0))
    
    # Rows processed
    if 'rows_processed' in metrics:
        rows_processed = Gauge('etl_job_rows_processed', 
                              'Number of rows processed',
                              ['job_name'], 
                              registry=registry)
        rows_processed.labels(job_name=metrics['job_name']).set(metrics['rows_processed'])
    
    push_to_gateway('localhost:9091', job='etl_scheduler', registry=registry)
    """
    pass


def send_to_datadog(metrics: Dict[str, Any]):
    """Send metrics to Datadog."""
    # This would send to Datadog in production
    # Example using datadog library:
    """
    from datadog import initialize, api, statsd
    
    # Send custom metric
    statsd.histogram('etl.job.execution_time',
                     metrics.get('execution_time', 0),
                     tags=[f"job:{metrics['job_name']}", 
                           f"status:{metrics['status']}"])
    
    if 'rows_processed' in metrics:
        statsd.gauge('etl.job.rows_processed',
                     metrics['rows_processed'],
                     tags=[f"job:{metrics['job_name']}"])
    
    # Send event for failures
    if metrics['status'] == 'failed':
        api.Event.create(
            title=f"ETL Job Failed: {metrics['job_name']}",
            text=metrics.get('error', 'Unknown error'),
            alert_type='error',
            tags=[f"job:{metrics['job_name']}"]
        )
    """
    pass


def send_slack_alert(alert_data: Dict[str, Any], urgent: bool = False):
    """Send alert to Slack channel."""
    webhook_url = MONITORING_CONFIG["slack_webhook"]
    if not webhook_url:
        return
    
    # Format message for Slack
    color = {
        "critical": "danger",
        "high": "danger",
        "medium": "warning",
        "low": "good"
    }.get(alert_data["severity"], "warning")
    
    slack_message = {
        "attachments": [{
            "color": color,
            "title": alert_data["subject"],
            "text": alert_data["message"],
            "fields": [
                {"title": "Severity", "value": alert_data["severity"], "short": True},
                {"title": "Host", "value": alert_data["hostname"], "short": True},
                {"title": "Time", "value": alert_data["timestamp"], "short": False}
            ],
            "footer": "KayGraph SQL Scheduler"
        }]
    }
    
    if urgent:
        slack_message["text"] = "<!channel> Urgent alert!"
    
    # In production, POST to webhook URL
    # import requests
    # requests.post(webhook_url, json=slack_message)
    
    logger.info(f"Would send Slack alert: {alert_data['subject']}")


def send_email_alert(alert_data: Dict[str, Any]):
    """Send email alert."""
    email_config = MONITORING_CONFIG["email_config"]
    
    # In production, use smtplib to send email
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    msg = MIMEMultipart()
    msg['From'] = email_config['from_email']
    msg['To'] = ', '.join(email_config['to_emails'])
    msg['Subject'] = f"[{alert_data['severity'].upper()}] {alert_data['subject']}"
    
    body = f"{alert_data['message']}\\n\\n"
    body += f"Severity: {alert_data['severity']}\\n"
    body += f"Host: {alert_data['hostname']}\\n"
    body += f"Time: {alert_data['timestamp']}\\n"
    
    if alert_data['metadata']:
        body += "\\nAdditional Information:\\n"
        for key, value in alert_data['metadata'].items():
            body += f"  {key}: {value}\\n"
    
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP(email_config['smtp_host'], email_config['smtp_port'])
    server.send_message(msg)
    server.quit()
    """
    
    logger.info(f"Would send email alert to {email_config['to_emails']}: {alert_data['subject']}")


def send_pagerduty_alert(alert_data: Dict[str, Any]):
    """Send alert to PagerDuty for critical issues."""
    integration_key = MONITORING_CONFIG["pagerduty_key"]
    if not integration_key:
        return
    
    # Format for PagerDuty Events API v2
    pagerduty_event = {
        "routing_key": integration_key,
        "event_action": "trigger",
        "payload": {
            "summary": alert_data["subject"],
            "source": alert_data["hostname"],
            "severity": "error" if alert_data["severity"] == "critical" else "warning",
            "custom_details": {
                "message": alert_data["message"],
                "metadata": alert_data["metadata"]
            }
        }
    }
    
    # In production, POST to PagerDuty API
    # import requests
    # requests.post("https://events.pagerduty.com/v2/enqueue", json=pagerduty_event)
    
    logger.info(f"Would send PagerDuty alert: {alert_data['subject']}")


class MetricsCollector:
    """Context manager for collecting execution metrics."""
    
    def __init__(self, job_name: str, operation: str):
        self.job_name = job_name
        self.operation = operation
        self.start_time = None
        self.metrics = {
            "job_name": job_name,
            "operation": operation
        }
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        self.metrics["execution_time"] = execution_time
        
        if exc_type is None:
            self.metrics["status"] = "success"
        else:
            self.metrics["status"] = "failed"
            self.metrics["error"] = str(exc_val)
            self.metrics["error_type"] = exc_type.__name__
        
        log_execution_metrics(self.metrics)
        
        # Don't suppress exceptions
        return False
    
    def add_metric(self, key: str, value: Any):
        """Add additional metric."""
        self.metrics[key] = value


def check_sla_compliance(job_name: str, execution_time: float) -> bool:
    """Check if job execution time meets SLA."""
    # Define SLAs for different jobs (in seconds)
    SLA_THRESHOLDS = {
        "daily_sales_etl": 3600,  # 1 hour
        "hourly_metrics": 300,    # 5 minutes
        "weekly_customer_summary": 7200  # 2 hours
    }
    
    threshold = SLA_THRESHOLDS.get(job_name, 3600)  # Default 1 hour
    
    if execution_time > threshold:
        send_alert(
            subject=f"SLA Breach: {job_name}",
            message=f"Job {job_name} took {execution_time:.2f}s, exceeding SLA of {threshold}s",
            severity="high",
            metadata={
                "execution_time": execution_time,
                "sla_threshold": threshold,
                "breach_amount": execution_time - threshold
            }
        )
        return False
    
    return True


if __name__ == "__main__":
    # Test monitoring functions
    logging.basicConfig(level=logging.INFO)
    
    setup_monitoring()
    
    # Test metrics logging
    test_metrics = {
        "job_name": "test_job",
        "status": "success",
        "execution_time": 45.2,
        "rows_processed": 1000
    }
    log_execution_metrics(test_metrics)
    
    # Test alerting
    send_alert(
        subject="Test Alert",
        message="This is a test alert from the monitoring system",
        severity="low"
    )
    
    # Test metrics collector
    with MetricsCollector("test_job", "test_operation") as collector:
        collector.add_metric("custom_metric", 42)
        time.sleep(0.1)  # Simulate some work
    
    print("Monitoring test completed")