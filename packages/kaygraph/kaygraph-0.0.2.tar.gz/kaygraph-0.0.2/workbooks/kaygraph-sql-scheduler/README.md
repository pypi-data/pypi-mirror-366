# KayGraph SQL Scheduler Example

This example demonstrates how to build a production-ready SQL execution system using KayGraph, with support for:
- Connection pooling and transaction management
- Scheduled execution via cron
- Error handling and retries
- Monitoring and alerting
- ETL pipeline patterns

## Architecture

The system consists of:
1. **SQLNode**: Base node for SQL execution with connection pooling
2. **ETL Pipeline**: Extract, Transform, Load workflow
3. **Scheduler**: External cron integration
4. **Monitoring**: Metrics collection and alerting

## Usage

### 1. Install Dependencies

```bash
pip install psycopg2-binary  # or your database driver
```

### 2. Configure Database

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "analytics",
    "user": "etl_user",
    "password": "secure_password"
}
```

### 3. Run Manually

```bash
python main.py
```

### 4. Schedule with Cron

```bash
# Run every hour
0 * * * * /usr/bin/python /path/to/main.py --job=hourly_sales_etl

# Run daily at 2 AM
0 2 * * * /usr/bin/python /path/to/main.py --job=daily_customer_summary
```

## Features

- **Connection Pooling**: Reuses database connections efficiently
- **Transaction Support**: Ensures data consistency
- **Error Recovery**: Automatic retries with exponential backoff
- **Monitoring**: Tracks query performance and failures
- **Flexible Scheduling**: Integrates with any scheduler (cron, Airflow, etc.)