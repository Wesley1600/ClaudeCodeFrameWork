"""
Sample Python file with intentional issues for testing validators
This file demonstrates various linting and formatting issues
"""

# Issue: unused import
import os
import sys
from typing import List

# Issue: inconsistent spacing around operators
x=5
y = 10+20

# Issue: line too long
very_long_variable_name = "This is a very long string that exceeds the recommended maximum line length of 88 characters (Black) or 79 (PEP 8) and should be wrapped"

# Issue: unused variable
unused_var = "This is never used"

# Issue: missing docstring
def add_numbers(a, b):
    return a + b

# Issue: inconsistent naming (should be snake_case)
def CalculateTotal(items):
    total = 0
    for item in items:
        total += item
    return total

# Issue: mutable default argument
def append_to_list(item, my_list=[]):
    my_list.append(item)
    return my_list

# Issue: bare except
def risky_operation():
    try:
        result = 10 / 0
        return result
    except:  # Should specify exception type
        return None

# Issue: missing type hints
def greet(name):
    return f"Hello {name}"

# Issue: inconsistent indentation (mixing spaces and tabs is caught but hard to see)
class SampleClass:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

# Issue: using deprecated/inefficient pattern
def filter_positive(numbers):
    result = []
    for num in numbers:
        if num > 0:
            result.append(num)
    return result

# Issue: multiple statements on one line
x = 1; y = 2; z = 3

# Issue: comparison to None using ==
def check_value(val):
    if val == None:  # Should use 'is None'
        return False
    return True

# Issue: not using context manager
def read_file(filename):
    f = open(filename, 'r')
    content = f.read()
    f.close()
    return content

# Good code for comparison
def calculate_price(quantity: int, price_per_item: float) -> float:
    """
    Calculate total price including shipping.

    Args:
        quantity: Number of items
        price_per_item: Price per individual item

    Returns:
        Total price including shipping

    Raises:
        ValueError: If quantity or price is negative
    """
    if quantity < 0 or price_per_item < 0:
        raise ValueError("Quantity and price must be non-negative")

    shipping_cost = 5.50
    return quantity * price_per_item + shipping_cost


def filter_positive_numbers(numbers: List[int]) -> List[int]:
    """Filter positive numbers using list comprehension."""
    return [num for num in numbers if num > 0]


def read_file_safely(filename: str) -> str:
    """Read file using context manager."""
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


if __name__ == "__main__":
    print(calculate_price(3, 9.99))
    print(filter_positive_numbers([1, -2, 3, -4, 5]))