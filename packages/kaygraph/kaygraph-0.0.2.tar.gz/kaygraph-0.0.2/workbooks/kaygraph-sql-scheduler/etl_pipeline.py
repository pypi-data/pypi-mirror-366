"""
Example ETL pipeline using KayGraph SQL nodes.
Demonstrates a real-world sales data processing workflow.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph, Node
from sql_nodes import SQLNode, BulkInsertNode

logger = logging.getLogger(__name__)


class ExtractSalesDataNode(SQLNode):
    """Extract raw sales data from source system."""
    
    def __init__(self):
        # Query to extract yesterday's sales
        query = """
            SELECT 
                s.sale_id,
                s.product_id,
                s.customer_id,
                s.quantity,
                s.unit_price,
                s.sale_date,
                s.store_id,
                p.category_id,
                p.product_name,
                c.customer_segment
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            JOIN customers c ON s.customer_id = c.customer_id
            WHERE s.sale_date >= %(start_date)s 
              AND s.sale_date < %(end_date)s
              AND s.status = 'completed'
            ORDER BY s.sale_date
        """
        super().__init__(
            query=query,
            timeout=300,  # 5 minute timeout for large extracts
            node_id="extract_sales"
        )
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare date range for extraction."""
        # Get date range from shared or calculate yesterday
        end_date = shared.get("end_date", datetime.utcnow().date())
        start_date = shared.get("start_date", end_date - timedelta(days=1))
        
        shared["extraction_dates"] = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        return {
            "query": self.query,
            "params": {
                "start_date": start_date,
                "end_date": end_date
            },
            "use_transaction": False,  # Read-only query
            "timeout": self.timeout
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store extracted data and check if we have results."""
        result = exec_res["result"]
        
        if result["row_count"] == 0:
            logger.warning("No sales data found for date range")
            return "no_data"
        
        # Convert to list of dicts for easier processing
        columns = result["columns"]
        rows = result["rows"]
        
        sales_data = [
            dict(zip(columns, row)) for row in rows
        ]
        
        shared["raw_sales_data"] = sales_data
        shared["extraction_stats"] = {
            "row_count": result["row_count"],
            "date_range": shared["extraction_dates"]
        }
        
        logger.info(f"Extracted {result['row_count']} sales records")
        return "transform"  # Go to transformation


class TransformSalesDataNode(Node):
    """Transform and enrich sales data."""
    
    def __init__(self):
        super().__init__(node_id="transform_sales")
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get raw sales data for transformation."""
        return shared.get("raw_sales_data", [])
    
    def exec(self, sales_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform sales data with business logic."""
        transformed_data = []
        aggregated_data = {}
        
        for sale in sales_data:
            # Calculate derived fields
            total_amount = sale["quantity"] * sale["unit_price"]
            
            # Apply business rules for margin calculation
            if sale["category_id"] in [1, 2, 3]:  # High margin categories
                margin = 0.40
            elif sale["category_id"] in [4, 5]:   # Medium margin
                margin = 0.25
            else:  # Low margin
                margin = 0.15
            
            profit = total_amount * margin
            
            # Transform record
            transformed_sale = {
                "sale_id": sale["sale_id"],
                "product_id": sale["product_id"],
                "customer_id": sale["customer_id"],
                "store_id": sale["store_id"],
                "sale_date": sale["sale_date"],
                "quantity": sale["quantity"],
                "unit_price": sale["unit_price"],
                "total_amount": round(total_amount, 2),
                "margin_rate": margin,
                "profit_amount": round(profit, 2),
                "customer_segment": sale["customer_segment"],
                "category_id": sale["category_id"]
            }
            
            transformed_data.append(transformed_sale)
            
            # Aggregate by store and date for summary
            key = (sale["store_id"], sale["sale_date"])
            if key not in aggregated_data:
                aggregated_data[key] = {
                    "store_id": sale["store_id"],
                    "sale_date": sale["sale_date"],
                    "total_sales": 0,
                    "total_profit": 0,
                    "transaction_count": 0,
                    "units_sold": 0
                }
            
            aggregated_data[key]["total_sales"] += total_amount
            aggregated_data[key]["total_profit"] += profit
            aggregated_data[key]["transaction_count"] += 1
            aggregated_data[key]["units_sold"] += sale["quantity"]
        
        # Round aggregated values
        for agg in aggregated_data.values():
            agg["total_sales"] = round(agg["total_sales"], 2)
            agg["total_profit"] = round(agg["total_profit"], 2)
            agg["avg_transaction_value"] = round(
                agg["total_sales"] / agg["transaction_count"], 2
            )
        
        return {
            "transformed_sales": transformed_data,
            "daily_summaries": list(aggregated_data.values())
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Dict[str, Any]) -> str:
        """Store transformed data."""
        shared["transformed_sales"] = exec_res["transformed_sales"]
        shared["daily_summaries"] = exec_res["daily_summaries"]
        
        logger.info(f"Transformed {len(exec_res['transformed_sales'])} sales records")
        logger.info(f"Generated {len(exec_res['daily_summaries'])} daily summaries")
        
        return "load"  # Go to load phase


class LoadSalesFactNode(BulkInsertNode):
    """Load transformed sales data into fact table."""
    
    def __init__(self):
        columns = [
            "sale_id", "product_id", "customer_id", "store_id",
            "sale_date", "quantity", "unit_price", "total_amount",
            "margin_rate", "profit_amount", "customer_segment", "category_id"
        ]
        super().__init__(
            table_name="sales_fact",
            columns=columns,
            batch_size=5000,
            node_id="load_sales_fact"
        )
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare sales data for bulk insert."""
        sales_data = shared.get("transformed_sales", [])
        
        # Convert to format expected by BulkInsertNode
        shared["bulk_data"] = sales_data
        
        return super().prep(shared)


class LoadDailySummaryNode(SQLNode):
    """Load or update daily summary table."""
    
    def __init__(self):
        # Upsert query for daily summaries
        query = """
            INSERT INTO daily_store_summary 
                (store_id, sale_date, total_sales, total_profit, 
                 transaction_count, units_sold, avg_transaction_value)
            VALUES 
                (%(store_id)s, %(sale_date)s, %(total_sales)s, %(total_profit)s,
                 %(transaction_count)s, %(units_sold)s, %(avg_transaction_value)s)
            ON CONFLICT (store_id, sale_date) 
            DO UPDATE SET
                total_sales = EXCLUDED.total_sales,
                total_profit = EXCLUDED.total_profit,
                transaction_count = EXCLUDED.transaction_count,
                units_sold = EXCLUDED.units_sold,
                avg_transaction_value = EXCLUDED.avg_transaction_value,
                last_updated = CURRENT_TIMESTAMP
        """
        super().__init__(
            query=query,
            node_id="load_daily_summary"
        )
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare to load each summary."""
        summaries = shared.get("daily_summaries", [])
        
        if not summaries:
            raise ValueError("No daily summaries to load")
        
        # We'll execute multiple times, once per summary
        shared["summaries_to_load"] = summaries
        shared["current_summary_index"] = 0
        
        return self._prep_single_summary(shared)
    
    def _prep_single_summary(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare a single summary for loading."""
        summaries = shared["summaries_to_load"]
        index = shared["current_summary_index"]
        
        if index >= len(summaries):
            return None
        
        return {
            "query": self.query,
            "params": summaries[index],
            "use_transaction": True,
            "timeout": self.timeout
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Move to next summary or complete."""
        shared["current_summary_index"] += 1
        
        if shared["current_summary_index"] < len(shared["summaries_to_load"]):
            # More summaries to load
            return "load_next_summary"
        
        logger.info(f"Loaded all {len(shared['summaries_to_load'])} daily summaries")
        return "validate"  # Go to validation


class ValidateETLNode(SQLNode):
    """Validate ETL results for data quality."""
    
    def __init__(self):
        query = """
            WITH source_totals AS (
                SELECT 
                    COUNT(*) as source_count,
                    SUM(quantity * unit_price) as source_total
                FROM sales
                WHERE sale_date >= %(start_date)s 
                  AND sale_date < %(end_date)s
                  AND status = 'completed'
            ),
            fact_totals AS (
                SELECT 
                    COUNT(*) as fact_count,
                    SUM(total_amount) as fact_total
                FROM sales_fact
                WHERE sale_date >= %(start_date)s 
                  AND sale_date < %(end_date)s
            )
            SELECT 
                s.source_count,
                f.fact_count,
                s.source_total,
                f.fact_total,
                ABS(s.source_count - f.fact_count) as count_diff,
                ABS(s.source_total - f.fact_total) as amount_diff
            FROM source_totals s, fact_totals f
        """
        super().__init__(
            query=query,
            node_id="validate_etl"
        )
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Use same date range as extraction."""
        dates = shared["extraction_dates"]
        return {
            "query": self.query,
            "params": dates,
            "use_transaction": False,
            "timeout": self.timeout
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Check validation results."""
        result = exec_res["result"]["rows"][0]
        
        validation_result = {
            "source_count": result[0],
            "fact_count": result[1],
            "source_total": float(result[2]) if result[2] else 0,
            "fact_total": float(result[3]) if result[3] else 0,
            "count_diff": result[4],
            "amount_diff": float(result[5]) if result[5] else 0
        }
        
        shared["validation_result"] = validation_result
        
        # Check thresholds
        if validation_result["count_diff"] > 0:
            logger.error(f"Row count mismatch: {validation_result['count_diff']} rows difference")
            return "validation_failed"
        
        if validation_result["amount_diff"] > 0.01:  # 1 cent tolerance
            logger.error(f"Amount mismatch: ${validation_result['amount_diff']} difference")
            return "validation_failed"
        
        logger.info("ETL validation passed successfully")
        return "cleanup"  # Success, go to cleanup


class CleanupNode(SQLNode):
    """Clean up old data based on retention policy."""
    
    def __init__(self):
        query = """
            DELETE FROM sales_fact
            WHERE sale_date < %(cutoff_date)s
            RETURNING COUNT(*) as deleted_count
        """
        super().__init__(
            query=query,
            node_id="cleanup_old_data"
        )
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cutoff date based on retention policy."""
        retention_days = shared.get("retention_days", 365)  # Default 1 year
        cutoff_date = datetime.utcnow().date() - timedelta(days=retention_days)
        
        return {
            "query": self.query,
            "params": {"cutoff_date": cutoff_date},
            "use_transaction": True,
            "timeout": self.timeout
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> None:
        """Log cleanup results."""
        if exec_res["result"]["row_count"] > 0:
            logger.info(f"Cleaned up {exec_res['result']['row_count']} old records")
        
        shared["etl_complete"] = True
        return None  # End of pipeline


class NoDataNode(Node):
    """Handle case when no data is found."""
    
    def __init__(self):
        super().__init__(node_id="handle_no_data")
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> None:
        """Log and set appropriate status."""
        logger.info("No data to process for date range")
        shared["etl_complete"] = True
        shared["etl_status"] = "no_data"
        return None


class ValidationFailedNode(Node):
    """Handle validation failures."""
    
    def __init__(self):
        super().__init__(node_id="handle_validation_failure")
    
    def exec(self, prep_res: Any) -> None:
        """Could send alerts, create tickets, etc."""
        # In production, you might:
        # - Send alert to ops team
        # - Create incident ticket
        # - Trigger data reconciliation job
        logger.error("ETL validation failed - manual intervention required")
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> None:
        """Set failure status."""
        shared["etl_complete"] = True
        shared["etl_status"] = "validation_failed"
        return None


def create_etl_pipeline() -> Graph:
    """Create the complete ETL pipeline graph."""
    # Create nodes
    extract = ExtractSalesDataNode()
    transform = TransformSalesDataNode()
    load_fact = LoadSalesFactNode()
    load_summary = LoadDailySummaryNode()
    validate = ValidateETLNode()
    cleanup = CleanupNode()
    no_data = NoDataNode()
    validation_failed = ValidationFailedNode()
    
    # Build graph with conditional paths
    graph = Graph(start=extract)
    
    # Main happy path
    extract - "transform" >> transform
    transform - "load" >> load_fact
    load_fact >> load_summary
    load_summary - "validate" >> validate
    validate - "cleanup" >> cleanup
    
    # Handle self-loop for multiple summaries
    load_summary - "load_next_summary" >> load_summary
    
    # Error paths
    extract - "no_data" >> no_data
    validate - "validation_failed" >> validation_failed
    
    return graph


if __name__ == "__main__":
    # Example usage
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # This would be your actual database config
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "analytics",
        "user": "etl_user",
        "password": "secure_password"
    }
    
    # Configure connection pool
    # SQLNode.configure_pool(db_config)
    
    # Create and run pipeline
    pipeline = create_etl_pipeline()
    
    # Shared context
    shared = {
        # Optionally override date range
        # "start_date": datetime(2024, 1, 1).date(),
        # "end_date": datetime(2024, 1, 2).date(),
        
        # Retention policy
        "retention_days": 365
    }
    
    # Run the pipeline
    # pipeline.run(shared)
    
    print("ETL pipeline created successfully")