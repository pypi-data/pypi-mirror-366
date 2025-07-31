#!/bin/bash
# Setup script for scheduling KayGraph SQL jobs with cron

# Create log directory
sudo mkdir -p /var/log/kaygraph
sudo chown $USER:$USER /var/log/kaygraph

# Create environment file for cron jobs
cat > /etc/kaygraph/etl.env << 'EOF'
# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=analytics
DB_USER=etl_user
DB_PASSWORD=secure_password
DB_SSLMODE=prefer

# Monitoring configuration
ALERT_WEBHOOK_URL=https://hooks.example.com/services/xxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
ALERT_FROM_EMAIL=etl@example.com
ALERT_TO_EMAILS=ops@example.com,data-team@example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=587

# PagerDuty for critical alerts
PAGERDUTY_INTEGRATION_KEY=xxx

# Python path
PYTHONPATH=/path/to/kaygraph
EOF

# Example crontab entries
cat > kaygraph_cron.txt << 'EOF'
# KayGraph SQL Scheduler Jobs
# m h  dom mon dow   command

# Environment setup
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

# Load environment variables
# Note: Adjust paths as needed

# Daily sales ETL - runs at 2 AM every day
0 2 * * * . /etc/kaygraph/etl.env && /usr/bin/python3 /path/to/kaygraph/workbooks/kaygraph-sql-scheduler/main.py --job=daily_sales_etl >> /var/log/kaygraph/daily_sales_etl.log 2>&1

# Hourly metrics aggregation - runs every hour at :15
15 * * * * . /etc/kaygraph/etl.env && /usr/bin/python3 /path/to/kaygraph/workbooks/kaygraph-sql-scheduler/main.py --job=hourly_metrics >> /var/log/kaygraph/hourly_metrics.log 2>&1

# Weekly customer summary - runs every Sunday at 3 AM
0 3 * * 0 . /etc/kaygraph/etl.env && /usr/bin/python3 /path/to/kaygraph/workbooks/kaygraph-sql-scheduler/main.py --job=weekly_customer_summary >> /var/log/kaygraph/weekly_customer_summary.log 2>&1

# Cleanup old logs - runs daily at 4 AM
0 4 * * * find /var/log/kaygraph -name "*.log" -mtime +30 -delete

# Health check - runs every 5 minutes
*/5 * * * * /path/to/kaygraph/workbooks/kaygraph-sql-scheduler/health_check.sh

EOF

echo "Cron setup script created. To install:"
echo "1. Edit /etc/kaygraph/etl.env with your configuration"
echo "2. Adjust paths in kaygraph_cron.txt"
echo "3. Run: crontab kaygraph_cron.txt"
echo ""
echo "To view current crontab: crontab -l"
echo "To edit crontab: crontab -e"