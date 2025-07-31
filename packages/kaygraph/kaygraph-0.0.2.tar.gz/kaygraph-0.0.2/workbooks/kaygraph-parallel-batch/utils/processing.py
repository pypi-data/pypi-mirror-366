"""
Processing utilities for parallel batch operations.
"""

import time
import random
import hashlib
import asyncio
from typing import Any, Dict, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


def simulate_io_operation(item: Any, duration: float = 0.5) -> Dict[str, Any]:
    """
    Simulate an I/O-bound operation (e.g., API call, file processing).
    
    Args:
        item: Item to process
        duration: Simulated operation duration
        
    Returns:
        Processing result
    """
    start_time = time.time()
    
    # Simulate I/O delay
    time.sleep(duration + random.uniform(-0.1, 0.1))
    
    # Simulate occasional failures
    if random.random() < 0.05:  # 5% failure rate
        raise Exception(f"Simulated failure for item: {item}")
    
    # Generate result
    result = {
        "item": item,
        "processed_at": time.time(),
        "duration": time.time() - start_time,
        "hash": hashlib.md5(str(item).encode()).hexdigest()[:8],
        "status": "success"
    }
    
    return result


async def simulate_async_io_operation(item: Any, duration: float = 0.5) -> Dict[str, Any]:
    """
    Simulate an async I/O-bound operation.
    
    Args:
        item: Item to process
        duration: Simulated operation duration
        
    Returns:
        Processing result
    """
    start_time = time.time()
    
    # Simulate async I/O delay
    await asyncio.sleep(duration + random.uniform(-0.1, 0.1))
    
    # Simulate occasional failures
    if random.random() < 0.05:  # 5% failure rate
        raise Exception(f"Simulated async failure for item: {item}")
    
    # Generate result
    result = {
        "item": item,
        "processed_at": time.time(),
        "duration": time.time() - start_time,
        "hash": hashlib.md5(str(item).encode()).hexdigest()[:8],
        "status": "success"
    }
    
    return result


def process_text_item(text: str) -> Dict[str, Any]:
    """
    Process a text item (word count, character analysis, etc.).
    
    Args:
        text: Text to process
        
    Returns:
        Analysis results
    """
    # Simulate processing time based on text length
    processing_time = min(0.1 + len(text) / 10000, 1.0)
    time.sleep(processing_time)
    
    # Perform analysis
    words = text.split()
    
    result = {
        "item": text[:50] + "..." if len(text) > 50 else text,
        "word_count": len(words),
        "char_count": len(text),
        "unique_words": len(set(words)),
        "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        "processing_time": processing_time
    }
    
    return result


def process_number_item(number: float) -> Dict[str, Any]:
    """
    Process a numeric item (calculations, transformations).
    
    Args:
        number: Number to process
        
    Returns:
        Calculation results
    """
    # Simulate complex calculation
    time.sleep(0.2)
    
    result = {
        "item": number,
        "square": number ** 2,
        "sqrt": number ** 0.5 if number >= 0 else None,
        "is_prime": is_prime(int(number)) if number.is_integer() and number > 0 else False,
        "factors": get_factors(int(number)) if number.is_integer() and number > 0 else []
    }
    
    return result


def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def get_factors(n: int) -> List[int]:
    """Get all factors of a number."""
    factors = []
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            factors.append(i)
            if i != n // i:
                factors.append(n // i)
    return sorted(factors)


def create_progress_callback(total_items: int) -> Callable[[int], None]:
    """
    Create a progress callback function.
    
    Args:
        total_items: Total number of items to process
        
    Returns:
        Progress callback function
    """
    processed = 0
    start_time = time.time()
    
    def callback(batch_size: int):
        nonlocal processed
        processed += batch_size
        
        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        eta = (total_items - processed) / rate if rate > 0 else 0
        
        progress = processed / total_items * 100
        logger.info(f"Progress: {progress:.1f}% ({processed}/{total_items}) "
                   f"Rate: {rate:.1f} items/sec, ETA: {eta:.1f}s")
    
    return callback


def calculate_optimal_batch_size(
    total_items: int,
    max_workers: int = None,
    target_batch_time: float = 1.0,
    item_process_time: float = 0.1
) -> int:
    """
    Calculate optimal batch size for parallel processing.
    
    Args:
        total_items: Total number of items
        max_workers: Maximum number of workers
        target_batch_time: Target time per batch
        item_process_time: Estimated time per item
        
    Returns:
        Optimal batch size
    """
    import os
    
    if max_workers is None:
        max_workers = os.cpu_count() or 4
    
    # Calculate based on target batch time
    batch_size = max(1, int(target_batch_time / item_process_time))
    
    # Ensure we have enough batches for all workers
    min_batches = max_workers * 2  # At least 2 batches per worker
    max_batch_size = max(1, total_items // min_batches)
    
    # Find balanced batch size
    batch_size = min(batch_size, max_batch_size)
    
    # Ensure reasonable limits
    batch_size = max(1, min(batch_size, 1000))
    
    logger.info(f"Calculated optimal batch size: {batch_size} "
                f"(items: {total_items}, workers: {max_workers})")
    
    return batch_size


class BatchProcessor:
    """Utility class for batch processing with progress tracking."""
    
    def __init__(self, process_func: Callable[[Any], Dict[str, Any]]):
        """
        Initialize batch processor.
        
        Args:
            process_func: Function to process individual items
        """
        self.process_func = process_func
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def process_item_with_error_handling(self, item: Any) -> Dict[str, Any]:
        """Process item with error handling."""
        try:
            result = self.process_func(item)
            result["status"] = "success"
            return result
        except Exception as e:
            error_result = {
                "item": item,
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }
            self.errors.append(error_result)
            return error_result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics."""
        if not self.start_time:
            return {}
        
        duration = (self.end_time or time.time()) - self.start_time
        total_processed = len(self.results)
        successful = sum(1 for r in self.results if r.get("status") == "success")
        
        return {
            "total_processed": total_processed,
            "successful": successful,
            "failed": len(self.errors),
            "success_rate": successful / total_processed if total_processed > 0 else 0,
            "total_duration": duration,
            "throughput": total_processed / duration if duration > 0 else 0,
            "avg_time_per_item": duration / total_processed if total_processed > 0 else 0
        }


if __name__ == "__main__":
    # Test processing functions
    logging.basicConfig(level=logging.INFO)
    
    # Test text processing
    text_result = process_text_item("Hello world this is a test")
    print("Text processing:", text_result)
    
    # Test number processing
    number_result = process_number_item(17)
    print("Number processing:", number_result)
    
    # Test batch size calculation
    batch_size = calculate_optimal_batch_size(1000, max_workers=8)
    print(f"Optimal batch size for 1000 items: {batch_size}")
    
    # Test progress callback
    callback = create_progress_callback(100)
    callback(25)
    callback(25)
    callback(50)