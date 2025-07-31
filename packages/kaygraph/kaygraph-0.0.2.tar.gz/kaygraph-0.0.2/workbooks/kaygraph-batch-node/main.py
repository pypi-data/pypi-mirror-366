"""
CSV chunk processing example using KayGraph BatchNode.

Demonstrates processing large CSV files by breaking them into
manageable chunks, calculating statistics for each chunk,
and aggregating the results.
"""

import os
import csv
import logging
from typing import List, Dict, Any, Iterator
from kaygraph import BatchNode, Graph, Node

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class GenerateSampleDataNode(Node):
    """Generate sample CSV data if not exists."""
    
    def prep(self, shared):
        """Check if data file exists."""
        return shared.get("csv_path", "sales_data.csv")
    
    def exec(self, csv_path):
        """Generate sample sales data."""
        if os.path.exists(csv_path):
            self.logger.info(f"Using existing CSV file: {csv_path}")
            return {"status": "exists", "path": csv_path}
        
        self.logger.info(f"Generating sample CSV data: {csv_path}")
        
        # Generate sample sales data
        import random
        from datetime import datetime, timedelta
        
        headers = ["transaction_id", "date", "product", "quantity", "price", "total"]
        products = ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Tool Z"]
        
        rows_to_generate = 10000  # Large enough to demonstrate chunking
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            base_date = datetime.now() - timedelta(days=365)
            
            for i in range(rows_to_generate):
                transaction_id = f"TXN{i+1:06d}"
                date = (base_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
                product = random.choice(products)
                quantity = random.randint(1, 20)
                price = round(random.uniform(10.0, 200.0), 2)
                total = round(quantity * price, 2)
                
                writer.writerow([transaction_id, date, product, quantity, price, total])
        
        self.logger.info(f"Generated {rows_to_generate} rows of sample data")
        return {"status": "generated", "path": csv_path, "rows": rows_to_generate}
    
    def post(self, shared, prep_res, exec_res):
        """Store file info."""
        shared["csv_info"] = exec_res
        return "default"


class CSVChunkReaderNode(Node):
    """Read CSV file and prepare chunks for processing."""
    
    def prep(self, shared):
        """Get CSV file path and chunk size."""
        return {
            "csv_path": shared.get("csv_path", "sales_data.csv"),
            "chunk_size": shared.get("chunk_size", 1000)
        }
    
    def exec(self, params):
        """Create chunk iterator."""
        csv_path = params["csv_path"]
        chunk_size = params["chunk_size"]
        
        # Count total rows (excluding header)
        with open(csv_path, 'r') as f:
            total_rows = sum(1 for line in f) - 1
        
        self.logger.info(f"Total rows in CSV: {total_rows}")
        self.logger.info(f"Chunk size: {chunk_size}")
        self.logger.info(f"Expected chunks: {(total_rows + chunk_size - 1) // chunk_size}")
        
        return {
            "csv_path": csv_path,
            "chunk_size": chunk_size,
            "total_rows": total_rows,
            "expected_chunks": (total_rows + chunk_size - 1) // chunk_size
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store chunk info."""
        shared["chunk_info"] = exec_res
        return "default"


class ProcessChunksBatchNode(BatchNode):
    """Process CSV file in chunks using batch processing."""
    
    def prep(self, shared):
        """Create iterator of chunks."""
        chunk_info = shared.get("chunk_info", {})
        csv_path = chunk_info.get("csv_path", "sales_data.csv")
        chunk_size = chunk_info.get("chunk_size", 1000)
        
        def chunk_generator():
            """Generate chunks of CSV data."""
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                chunk = []
                chunk_num = 0
                
                for row in reader:
                    chunk.append(row)
                    
                    if len(chunk) >= chunk_size:
                        chunk_num += 1
                        yield {
                            "chunk_id": chunk_num,
                            "data": chunk,
                            "size": len(chunk)
                        }
                        chunk = []
                
                # Yield remaining rows
                if chunk:
                    chunk_num += 1
                    yield {
                        "chunk_id": chunk_num,
                        "data": chunk,
                        "size": len(chunk)
                    }
        
        # Return the generator
        return chunk_generator()
    
    def exec(self, chunk_data):
        """Process a single chunk."""
        chunk_id = chunk_data["chunk_id"]
        data = chunk_data["data"]
        size = chunk_data["size"]
        
        self.logger.info(f"Processing chunk {chunk_id} with {size} rows")
        
        # Calculate statistics for this chunk
        total_sales = 0
        product_sales = {}
        
        for row in data:
            try:
                total = float(row["total"])
                total_sales += total
                
                product = row["product"]
                if product not in product_sales:
                    product_sales[product] = {"count": 0, "total": 0}
                
                product_sales[product]["count"] += 1
                product_sales[product]["total"] += total
                
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error processing row in chunk {chunk_id}: {e}")
        
        # Return chunk statistics
        return {
            "chunk_id": chunk_id,
            "rows_processed": size,
            "total_sales": round(total_sales, 2),
            "average_sale": round(total_sales / size, 2) if size > 0 else 0,
            "product_breakdown": product_sales
        }
    
    def post(self, shared, prep_res, exec_res):
        """Aggregate results from all chunks."""
        # Aggregate statistics
        total_rows = 0
        grand_total_sales = 0
        all_product_sales = {}
        chunk_count = len(exec_res)
        
        for chunk_result in exec_res:
            total_rows += chunk_result["rows_processed"]
            grand_total_sales += chunk_result["total_sales"]
            
            # Merge product sales
            for product, stats in chunk_result["product_breakdown"].items():
                if product not in all_product_sales:
                    all_product_sales[product] = {"count": 0, "total": 0}
                
                all_product_sales[product]["count"] += stats["count"]
                all_product_sales[product]["total"] += stats["total"]
        
        # Calculate final statistics
        summary = {
            "chunks_processed": chunk_count,
            "total_rows": total_rows,
            "total_sales": round(grand_total_sales, 2),
            "average_sale": round(grand_total_sales / total_rows, 2) if total_rows > 0 else 0,
            "products": {}
        }
        
        # Add product statistics
        for product, stats in all_product_sales.items():
            summary["products"][product] = {
                "transactions": stats["count"],
                "total_sales": round(stats["total"], 2),
                "average_sale": round(stats["total"] / stats["count"], 2) if stats["count"] > 0 else 0,
                "percentage": round((stats["total"] / grand_total_sales) * 100, 2) if grand_total_sales > 0 else 0
            }
        
        # Save summary
        import json
        with open("sales_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        shared["sales_summary"] = summary
        
        # Print results
        print(f"\n📊 Sales Analysis Summary")
        print(f"  - Chunks processed: {summary['chunks_processed']}")
        print(f"  - Total transactions: {summary['total_rows']:,}")
        print(f"  - Total sales: ${summary['total_sales']:,.2f}")
        print(f"  - Average sale: ${summary['average_sale']:.2f}")
        
        print(f"\n📈 Product Breakdown:")
        for product, stats in sorted(summary["products"].items(), 
                                   key=lambda x: x[1]["total_sales"], 
                                   reverse=True):
            print(f"  - {product}:")
            print(f"    • Transactions: {stats['transactions']:,}")
            print(f"    • Total: ${stats['total_sales']:,.2f} ({stats['percentage']}%)")
            print(f"    • Average: ${stats['average_sale']:.2f}")
        
        return None


def create_csv_processing_graph():
    """Create graph for CSV chunk processing."""
    # Create nodes
    data_gen = GenerateSampleDataNode(node_id="data_generator")
    chunk_reader = CSVChunkReaderNode(node_id="chunk_reader")
    processor = ProcessChunksBatchNode(node_id="chunk_processor")
    
    # Connect nodes
    data_gen >> chunk_reader >> processor
    
    return Graph(start=data_gen)


def main():
    """Run the CSV chunk processing example."""
    print("📊 KayGraph CSV Chunk Processing Example")
    print("=" * 50)
    print("This example demonstrates processing large CSV files")
    print("by breaking them into manageable chunks.\n")
    
    # Create graph
    graph = create_csv_processing_graph()
    
    # Configuration
    shared = {
        "csv_path": "sales_data.csv",
        "chunk_size": 1000  # Process 1000 rows at a time
    }
    
    print(f"Configuration:")
    print(f"  - CSV file: {shared['csv_path']}")
    print(f"  - Chunk size: {shared['chunk_size']} rows\n")
    
    # Run the graph
    import time
    start_time = time.time()
    
    graph.run(shared)
    
    end_time = time.time()
    
    print(f"\n⏱️  Total processing time: {end_time - start_time:.2f} seconds")
    
    # Show chunk processing benefits
    chunk_info = shared.get("chunk_info", {})
    if chunk_info:
        print(f"\n💡 Chunk Processing Benefits:")
        print(f"  - Memory efficient: Only {shared['chunk_size']} rows in memory at once")
        print(f"  - Progress tracking: Can monitor each chunk")
        print(f"  - Error isolation: Failures affect only one chunk")
        print(f"  - Parallelizable: Chunks can be processed concurrently")


if __name__ == "__main__":
    main()