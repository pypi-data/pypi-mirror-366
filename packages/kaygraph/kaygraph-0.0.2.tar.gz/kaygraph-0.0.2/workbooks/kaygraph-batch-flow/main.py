"""
Batch Flow example using KayGraph.

Demonstrates using BatchGraph to apply multiple image filters
to multiple images by wrapping a base graph in batch processing.
"""

import os
import logging
from typing import List, Dict, Any, Tuple
from kaygraph import Node, Graph, BatchGraph, MetricsNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# Base graph nodes for single image processing

class LoadImageNode(Node):
    """Load an image file."""
    
    def prep(self, shared):
        """Get image path from parameters."""
        # BatchGraph passes parameters via self.params
        return self.params.get("image_path")
    
    def exec(self, image_path):
        """Load image (mock implementation)."""
        self.logger.info(f"Loading image: {image_path}")
        
        # Mock image loading - in real implementation use PIL/OpenCV
        if not os.path.exists(image_path):
            # Create mock image data
            return {
                "path": image_path,
                "width": 1920,
                "height": 1080,
                "format": "JPEG",
                "data": f"[Mock image data for {os.path.basename(image_path)}]"
            }
        
        # For existing files, return mock data
        return {
            "path": image_path,
            "width": 1920,
            "height": 1080,
            "format": os.path.splitext(image_path)[1][1:].upper(),
            "data": f"[Loaded image data from {os.path.basename(image_path)}]"
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store loaded image."""
        shared["loaded_image"] = exec_res
        return "default"


class ApplyFilterNode(MetricsNode):
    """Apply a filter to the image."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(collect_metrics=True, *args, **kwargs)
    
    def prep(self, shared):
        """Get image and filter info."""
        return {
            "image": shared.get("loaded_image"),
            "filter": self.params.get("filter_type", "none")
        }
    
    def exec(self, data):
        """Apply the specified filter."""
        image = data["image"]
        filter_type = data["filter"]
        
        self.logger.info(f"Applying {filter_type} filter to {os.path.basename(image['path'])}")
        
        # Mock filter application
        import time
        
        # Different filters take different amounts of time
        filter_times = {
            "blur": 0.3,
            "sharpen": 0.2,
            "grayscale": 0.1,
            "sepia": 0.15,
            "edge_detect": 0.4,
            "none": 0.05
        }
        
        processing_time = filter_times.get(filter_type, 0.1)
        time.sleep(processing_time)  # Simulate processing
        
        # Create filtered image data
        filtered_image = image.copy()
        filtered_image["filter_applied"] = filter_type
        filtered_image["data"] = f"[{filter_type.upper()} filtered: {image['data']}]"
        filtered_image["processing_time"] = processing_time
        
        return filtered_image
    
    def post(self, shared, prep_res, exec_res):
        """Store filtered image."""
        shared["filtered_image"] = exec_res
        return "default"


class SaveImageNode(Node):
    """Save the processed image."""
    
    def prep(self, shared):
        """Get filtered image and output path."""
        return {
            "image": shared.get("filtered_image"),
            "output_dir": self.params.get("output_dir", "output")
        }
    
    def exec(self, data):
        """Save the image."""
        image = data["image"]
        output_dir = data["output_dir"]
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        original_name = os.path.basename(image["path"])
        name_parts = os.path.splitext(original_name)
        output_name = f"{name_parts[0]}_{image['filter_applied']}{name_parts[1]}"
        output_path = os.path.join(output_dir, output_name)
        
        # Mock save operation
        self.logger.info(f"Saving filtered image to: {output_path}")
        
        # In real implementation, save actual image file
        # For demo, create a text file describing the operation
        with open(output_path + ".txt", 'w') as f:
            f.write(f"Image Processing Summary\n")
            f.write(f"=======================\n\n")
            f.write(f"Original: {image['path']}\n")
            f.write(f"Filter: {image['filter_applied']}\n")
            f.write(f"Dimensions: {image['width']}x{image['height']}\n")
            f.write(f"Processing Time: {image['processing_time']}s\n")
            f.write(f"Output: {output_path}\n")
        
        return {
            "original": image["path"],
            "filter": image["filter_applied"],
            "output": output_path,
            "success": True
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store save result."""
        shared["save_result"] = exec_res
        return None


def create_base_image_graph():
    """Create the base graph for processing a single image."""
    # Create nodes
    loader = LoadImageNode(node_id="loader")
    filter_node = ApplyFilterNode(node_id="filter")
    saver = SaveImageNode(node_id="saver")
    
    # Connect nodes
    loader >> filter_node >> saver
    
    return Graph(start=loader)


# Batch processing wrapper

class ImageBatchGraph(BatchGraph):
    """Process multiple images with multiple filters."""
    
    def __init__(self, base_graph: Graph, *args, **kwargs):
        """Initialize with the base graph."""
        super().__init__(base_graph, *args, **kwargs)
    
    def prep(self, shared):
        """Generate all image-filter combinations."""
        # Get images and filters from shared context
        images = shared.get("images", [])
        filters = shared.get("filters", [])
        output_dir = shared.get("output_dir", "output")
        
        # Generate parameter sets for each combination
        param_sets = []
        for image_path in images:
            for filter_type in filters:
                params = {
                    "image_path": image_path,
                    "filter_type": filter_type,
                    "output_dir": output_dir
                }
                param_sets.append(params)
        
        self.logger.info(f"Created {len(param_sets)} processing tasks")
        self.logger.info(f"  - {len(images)} images × {len(filters)} filters")
        
        return param_sets
    
    def exec(self, params):
        """Execute base graph with specific parameters."""
        # This is handled by parent BatchGraph
        # It sets self.base_graph.params and runs the graph
        return super().exec(params)
    
    def post(self, shared, prep_res, exec_res):
        """Aggregate results from all image processing."""
        # Create summary
        total_processed = len(exec_res)
        successful = sum(1 for r in exec_res if r.get("shared", {}).get("save_result", {}).get("success"))
        
        # Group by filter
        by_filter = {}
        for result in exec_res:
            save_result = result.get("shared", {}).get("save_result", {})
            if save_result:
                filter_type = save_result.get("filter", "unknown")
                if filter_type not in by_filter:
                    by_filter[filter_type] = []
                by_filter[filter_type].append(save_result)
        
        # Collect metrics
        all_metrics = []
        for result in exec_res:
            if "metrics" in result:
                all_metrics.extend(result["metrics"])
        
        # Calculate average processing time per filter
        filter_times = {}
        for metrics in all_metrics:
            if metrics["node_id"] == "filter":
                filter_type = metrics.get("filter_type", "unknown")
                if filter_type not in filter_times:
                    filter_times[filter_type] = []
                filter_times[filter_type].append(metrics["duration"])
        
        summary = {
            "total_tasks": total_processed,
            "successful": successful,
            "failed": total_processed - successful,
            "filters_applied": list(by_filter.keys()),
            "output_directory": shared.get("output_dir", "output"),
            "average_times_by_filter": {
                f: sum(times)/len(times) for f, times in filter_times.items()
            }
        }
        
        shared["batch_summary"] = summary
        
        # Print summary
        print(f"\n✅ Batch Processing Complete!")
        print(f"  - Total tasks: {summary['total_tasks']}")
        print(f"  - Successful: {summary['successful']}")
        print(f"  - Failed: {summary['failed']}")
        
        print(f"\n⏱️  Average Processing Times by Filter:")
        for filter_type, avg_time in summary['average_times_by_filter'].items():
            print(f"  - {filter_type}: {avg_time:.3f}s")
        
        print(f"\n📁 Output saved to: {summary['output_directory']}/")
        
        return None


def main():
    """Run the batch flow image processing example."""
    print("🖼️  KayGraph Batch Flow - Image Processing")
    print("=" * 50)
    print("This example demonstrates using BatchGraph to apply")
    print("multiple filters to multiple images.\n")
    
    # Create test images (mock)
    test_images = [
        "images/photo1.jpg",
        "images/photo2.jpg",
        "images/landscape.png",
        "images/portrait.png"
    ]
    
    # Available filters
    filters = ["blur", "sharpen", "grayscale", "sepia", "edge_detect"]
    
    # Create base graph for single image processing
    base_graph = create_base_image_graph()
    
    # Wrap in batch graph
    batch_graph = ImageBatchGraph(base_graph, graph_id="image_batch")
    
    # Shared context
    shared = {
        "images": test_images,
        "filters": filters,
        "output_dir": "processed_images"
    }
    
    print(f"Configuration:")
    print(f"  - Images: {len(test_images)}")
    print(f"  - Filters: {', '.join(filters)}")
    print(f"  - Total combinations: {len(test_images) * len(filters)}")
    print(f"  - Output directory: {shared['output_dir']}/\n")
    
    # Run batch processing
    import time
    start_time = time.time()
    
    result = batch_graph.run(shared)
    
    end_time = time.time()
    
    print(f"\n⏱️  Total processing time: {end_time - start_time:.2f} seconds")
    
    # Calculate theoretical speedup with parallel processing
    summary = shared.get("batch_summary", {})
    if summary and summary.get("average_times_by_filter"):
        total_sequential_time = sum(
            len(test_images) * avg_time 
            for avg_time in summary["average_times_by_filter"].values()
        )
        print(f"\n💡 Performance Analysis:")
        print(f"  - Sequential time (if processed one by one): {total_sequential_time:.2f}s")
        print(f"  - Actual time: {end_time - start_time:.2f}s")
        print(f"  - Note: For parallel processing, see kaygraph-parallel-batch-flow")


if __name__ == "__main__":
    main()