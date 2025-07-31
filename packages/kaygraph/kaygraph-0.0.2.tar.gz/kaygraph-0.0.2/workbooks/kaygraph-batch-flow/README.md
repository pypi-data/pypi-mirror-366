# KayGraph Batch Flow - Image Processing Pipeline

Demonstrates using BatchGraph to wrap an entire graph for batch processing. This example shows how to apply multiple image filters to multiple images by running a base graph many times with different parameters.

## What it does

This example showcases:
- **BatchGraph Pattern**: Wrap existing graphs for batch execution
- **Parameter Injection**: Pass different parameters to each graph run
- **Cartesian Product**: Process all combinations of images × filters
- **Result Aggregation**: Collect and summarize results from all runs

## Features

- Base graph for single image processing (Load → Filter → Save)
- Batch wrapper that generates all image-filter combinations
- Metrics collection for performance analysis
- Organized output with clear naming conventions

## How to run

```bash
python main.py
```

## Architecture

### Base Graph (Single Image)
```
LoadImageNode → ApplyFilterNode → SaveImageNode
      ↓                ↓                ↓
 Load image      Apply filter      Save result
```

### Batch Wrapper
```
ImageBatchGraph
    ├── prep() → Generate (image, filter) combinations
    ├── exec() → Run base graph for each combination
    └── post() → Aggregate all results
```

## The BatchGraph Pattern

```python
# 1. Create a base graph for single item processing
base_graph = create_single_item_graph()

# 2. Wrap it in BatchGraph
batch_graph = BatchGraph(base_graph)

# 3. BatchGraph automatically:
#    - Calls prep() to get parameter sets
#    - Runs base graph for each parameter set
#    - Collects results in post()
```

## Parameter Passing

BatchGraph passes parameters via `self.params` in nodes:

```python
class LoadImageNode(Node):
    def prep(self, shared):
        # Get parameter from BatchGraph
        return self.params.get("image_path")
```

## Example Output

```
🖼️  KayGraph Batch Flow - Image Processing
==================================================
This example demonstrates using BatchGraph to apply
multiple filters to multiple images.

Configuration:
  - Images: 4
  - Filters: blur, sharpen, grayscale, sepia, edge_detect
  - Total combinations: 20
  - Output directory: processed_images/

[INFO] Created 20 processing tasks
[INFO]   - 4 images × 5 filters
[INFO] Loading image: images/photo1.jpg
[INFO] Applying blur filter to photo1.jpg
[INFO] Saving filtered image to: processed_images/photo1_blur.jpg
...

✅ Batch Processing Complete!
  - Total tasks: 20
  - Successful: 20
  - Failed: 0

⏱️  Average Processing Times by Filter:
  - blur: 0.300s
  - sharpen: 0.200s
  - grayscale: 0.100s
  - sepia: 0.150s
  - edge_detect: 0.400s

📁 Output saved to: processed_images/

⏱️  Total processing time: 23.45 seconds

💡 Performance Analysis:
  - Sequential time (if processed one by one): 23.00s
  - Actual time: 23.45s
  - Note: For parallel processing, see kaygraph-parallel-batch-flow
```

## Output Structure

```
processed_images/
├── photo1_blur.jpg.txt
├── photo1_sharpen.jpg.txt
├── photo1_grayscale.jpg.txt
├── photo1_sepia.jpg.txt
├── photo1_edge_detect.jpg.txt
├── photo2_blur.jpg.txt
├── photo2_sharpen.jpg.txt
...
```

## Use Cases

- **Image Processing**: Apply multiple filters/effects
- **Document Processing**: Convert documents to multiple formats
- **Data Pipeline**: Run same pipeline with different configurations
- **A/B Testing**: Test multiple variations of a process
- **Report Generation**: Generate reports for multiple entities

## Comparison with BatchNode

| Feature | BatchNode | BatchGraph |
|---------|-----------|------------|
| Use Case | Process list items | Run entire graphs |
| Granularity | Single node | Full graph |
| State Management | Shared across items | Isolated per run |
| Parameter Passing | Via exec() | Via self.params |
| Best For | Simple transformations | Complex pipelines |

## Customization

### Adding New Filters

```python
# In ApplyFilterNode.exec()
filter_times = {
    "blur": 0.3,
    "vintage": 0.25,  # Add new filter
    "cartoon": 0.5,   # Add new filter
    ...
}
```

### Custom Parameter Generation

```python
# In ImageBatchGraph.prep()
# Instead of cartesian product, use custom logic
param_sets = []
for i, image in enumerate(images):
    # Apply different filters to different images
    if i % 2 == 0:
        param_sets.append({"image": image, "filter": "blur"})
    else:
        param_sets.append({"image": image, "filter": "sharpen"})
```

## Performance Considerations

Sequential processing can be slow for I/O-bound operations. For better performance:
- Use `ParallelBatchGraph` for concurrent execution
- Consider async operations for I/O-heavy tasks
- Implement proper error handling for partial failures