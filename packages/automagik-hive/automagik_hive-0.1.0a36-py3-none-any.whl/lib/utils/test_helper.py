"""Test helper utilities for the Automagik Hive project."""

def calculate_score(value: int) -> int:
    """Calculate a test score based on input value."""
    return value * 2 + 10

def format_message(msg: str) -> str:
    """Format a message with proper casing."""
    return msg.strip().title()