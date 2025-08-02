"""Math helper utilities for calculations."""

def calculate_factorial(n: int) -> int:
    """Calculate factorial of a number."""
    if n < 0:
        raise ValueError("Cannot calculate factorial of negative number")
    if n == 0 or n == 1:
        return 1
    return n * calculate_factorial(n - 1)