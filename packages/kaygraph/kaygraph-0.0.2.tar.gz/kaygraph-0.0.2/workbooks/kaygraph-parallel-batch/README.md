# KayGraph Parallel Batch Processing

This workbook demonstrates parallel batch processing using KayGraph, showing significant performance improvements for I/O-bound and CPU-bound workloads.

## What it does

The parallel batch system:
- Compares sequential vs parallel processing performance
- Automatically calculates optimal batch sizes
- Handles different types of workloads (I/O, text, numeric)
- Provides detailed performance metrics and speedup analysis
- Ensures result correctness across processing modes

## How to run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run comparison (sequential vs parallel):
```bash
# Process 100 items with default workers
python main.py compare 100

# Process 500 items with 16 workers
python main.py compare 500 16
```

3. Run parallel processing only:
```bash
# Process 1000 items
python main.py parallel 1000

# Process 5000 items with 32 workers
python main.py parallel 5000 32
```

4. Run benchmarks:
```bash
python main.py benchmark
```

## How it works

### Graph Structure

#### Comparison Graph
```
LoadDataNode → SplitBatchNode → SequentialProcessNode
                                         ↓
                                  ParallelProcessNode
                                         ↓
                                   AggregateNode → ReportNode
```

#### Parallel-Only Graph
```
LoadDataNode → SplitBatchNode → ParallelProcessNode → ReportNode
```

### Key Components

1. **LoadDataNode**: 
   - Generates test data (numbers, text, mixed)
   - Configurable data types and sizes

2. **SplitBatchNode**: 
   - Calculates optimal batch size
   - Considers worker count and workload type
   - Balances load across workers

3. **ParallelBatchNode**: 
   - Uses ThreadPoolExecutor for parallelism
   - Processes batches concurrently
   - Includes progress tracking

4. **AggregateNode**: 
   - Compares results between modes
   - Calculates speedup and efficiency
   - Verifies correctness

### Features from KayGraph

- **ParallelBatchNode**: Built-in parallel processing
- **BatchNode**: Sequential batch processing
- **MetricsNode**: Performance measurement
- **Automatic batching**: Via prep() method

## Performance Results

### Typical Speedups

| Workload Type | Items | Workers | Speedup |
|--------------|-------|---------|---------|
| I/O-bound    | 100   | 8       | 5-7x    |
| I/O-bound    | 1000  | 16      | 10-14x  |
| Text processing | 500 | 4       | 3-4x    |
| CPU-bound    | 100   | 4       | 2-3x    |

### Example Output

```
Parallel Batch Processing Performance Report
===========================================

Data Summary:
- Total items: 200
- Data type: numbers
- Batch size: 25
- Number of batches: 8

Performance Results:
- Sequential processing time: 100.43s
- Parallel processing time: 13.21s
- Speedup: 7.60x
- Efficiency: 95.0%

Throughput:
- Sequential: 2.0 items/sec
- Parallel: 15.1 items/sec

Correctness:
- Results match: ✓
- Sequential errors: 10
- Parallel errors: 10

Conclusion:
Parallel processing provided significant speedup (7.6x faster)!
```

## Workload Types

### I/O-Bound (Default)
Simulates API calls, database queries, file operations:
- 0.5s average latency per item
- High parallelization benefit
- Minimal CPU usage

### Text Processing
Analyzes text content:
- Word count, unique words
- Character analysis
- Moderate parallelization benefit

### Numeric Processing
CPU-intensive calculations:
- Prime checking
- Factor calculation
- Lower parallelization benefit

## Optimization Tips

### Batch Size Selection
The system automatically calculates optimal batch size based on:
- Total items
- Available workers
- Expected processing time
- Memory constraints

### Worker Count
- **I/O-bound**: 2-4x CPU cores
- **CPU-bound**: 1x CPU cores
- **Mixed**: 1.5-2x CPU cores

### Progress Tracking
Built-in progress callbacks show:
- Items processed
- Processing rate
- ETA calculation

## Advanced Usage

### Custom Processing Functions

```python
def custom_process(item):
    # Your processing logic
    result = expensive_operation(item)
    return {"item": item, "result": result}

# Use in nodes
processor = BatchProcessor(custom_process)
```

### Error Handling
- Individual item failures don't stop batch
- Error tracking and reporting
- Configurable retry logic

### Memory Management
- Streaming results to avoid memory buildup
- Configurable batch sizes
- Garbage collection between batches

## Benchmarking

The benchmark mode tests various scenarios:

1. **Small I/O-bound**: Quick validation
2. **Large I/O-bound**: Maximum speedup demo
3. **Text processing**: Real-world use case
4. **Numeric calculations**: CPU-bound scenario

Results help determine optimal configuration for your workload.

## Use Cases

- **API Data Collection**: Parallel API calls
- **File Processing**: Concurrent file operations
- **Data Transformation**: Batch ETL pipelines
- **Image Processing**: Parallel image filters
- **Report Generation**: Concurrent report creation
- **Web Scraping**: Parallel page fetching

## Troubleshooting

### Low Speedup
- Check if workload is truly parallelizable
- Verify optimal worker count
- Consider I/O vs CPU bottlenecks

### Memory Issues
- Reduce batch size
- Process results incrementally
- Use generator patterns

### Result Mismatches
- Check for race conditions
- Ensure deterministic processing
- Verify thread safety