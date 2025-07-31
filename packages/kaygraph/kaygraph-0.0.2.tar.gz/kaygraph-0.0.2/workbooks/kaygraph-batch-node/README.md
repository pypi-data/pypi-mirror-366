# KayGraph Batch Node - CSV Chunk Processing

Demonstrates processing large CSV files in chunks using KayGraph's BatchNode, showing how to handle large datasets efficiently without loading everything into memory.

## What it does

This example shows how to:
- **Process Large Files**: Break CSV files into manageable chunks
- **Calculate Statistics**: Compute sales metrics for each chunk
- **Aggregate Results**: Combine chunk results into final summary
- **Memory Efficiency**: Process millions of rows with limited memory

## Features

- Generates sample sales data if not present
- Processes CSV in configurable chunk sizes
- Calculates per-chunk and total statistics
- Produces detailed product breakdown
- Demonstrates iterator-based batch processing

## How to run

```bash
python main.py
```

## Architecture

```
GenerateSampleDataNode → CSVChunkReaderNode → ProcessChunksBatchNode
         ↓                      ↓                        ↓
   Create sample CSV    Prepare chunk info      Process each chunk
                                               and aggregate results
```

### Node Details

1. **GenerateSampleDataNode**: Creates 10,000 row sample CSV if needed
2. **CSVChunkReaderNode**: Analyzes file and prepares chunking parameters
3. **ProcessChunksBatchNode**: 
   - `prep()`: Returns chunk generator (iterator)
   - `exec()`: Processes individual chunks
   - `post()`: Aggregates all chunk results

## Chunk Processing Pattern

```python
# In prep() - return an iterator
def chunk_generator():
    with open(csv_path, 'r') as f:
        chunk = []
        for row in reader:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []

# BatchNode automatically calls exec() for each yielded item
```

## Example Output

```
📊 KayGraph CSV Chunk Processing Example
==================================================
This example demonstrates processing large CSV files
by breaking them into manageable chunks.

Configuration:
  - CSV file: sales_data.csv
  - Chunk size: 1000 rows

[INFO] Generating sample CSV data: sales_data.csv
[INFO] Generated 10000 rows of sample data
[INFO] Total rows in CSV: 10000
[INFO] Chunk size: 1000
[INFO] Expected chunks: 10
[INFO] Processing chunk 1 with 1000 rows
[INFO] Processing chunk 2 with 1000 rows
...

📊 Sales Analysis Summary
  - Chunks processed: 10
  - Total transactions: 10,000
  - Total sales: $1,053,234.56
  - Average sale: $105.32

📈 Product Breakdown:
  - Widget A:
    • Transactions: 2,043
    • Total: $215,432.10 (20.5%)
    • Average: $105.44
  - Gadget X:
    • Transactions: 1,987
    • Total: $209,876.54 (19.9%)
    • Average: $105.61
...

⏱️  Total processing time: 2.34 seconds

💡 Chunk Processing Benefits:
  - Memory efficient: Only 1000 rows in memory at once
  - Progress tracking: Can monitor each chunk
  - Error isolation: Failures affect only one chunk
  - Parallelizable: Chunks can be processed concurrently
```

## Use Cases

- **Large CSV/Excel Processing**: Financial data, logs, exports
- **Database Table Processing**: Process tables in batches
- **API Pagination**: Handle paginated API responses
- **Stream Processing**: Process continuous data streams
- **ETL Pipelines**: Extract-Transform-Load operations

## Memory Efficiency

Traditional approach loads entire file:
```python
# Bad for large files - loads everything
df = pd.read_csv("huge_file.csv")  # 🚫 May run out of memory
```

Chunk processing approach:
```python
# Good - processes in small pieces
for chunk in pd.read_csv("huge_file.csv", chunksize=1000):
    process(chunk)  # ✅ Memory efficient
```

## Customization

Adjust chunk size based on:
- Available memory
- Row complexity
- Processing requirements
- Network/API constraints

```python
shared = {
    "chunk_size": 5000  # Larger chunks for simple data
}
```