"""
Create a function to calculate fibonacci numbers

Generated on: 2025-07-23
"""

from functools import lru_cache


@lru_cache(maxsize=None)
def calculate_fibonacci_numbers(n):
    """
    Create a function to calculate fibonacci numbers
    
    Args:
        n: Parameter description
    """
    if n < 0:
        raise ValueError("Input must be non-negative")
    if n <= 1:
        return n
    return nfibonacci(n - 1) + nfibonacci(n - 2)