"""
Example Python code for testing the code translation skill.
This module contains utility functions for string manipulation.
"""

def reverse_string(text):
    """
    Reverse a string.

    Args:
        text (str): The string to reverse

    Returns:
        str: The reversed string
    """
    return text[::-1]


def is_palindrome(text):
    """
    Check if a string is a palindrome (reads the same forwards and backwards).

    Args:
        text (str): The string to check

    Returns:
        bool: True if palindrome, False otherwise
    """
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]


def count_vowels(text):
    """
    Count the number of vowels in a string.

    Args:
        text (str): The string to analyze

    Returns:
        int: The number of vowels found
    """
    vowels = "aeiouAEIOU"
    return sum(1 for char in text if char in vowels)


if __name__ == "__main__":
    # Simple tests
    print("Testing reverse_string:")
    assert reverse_string("hello") == "olleh"
    assert reverse_string("") == ""
    print("✓ reverse_string tests passed")

    print("\nTesting is_palindrome:")
    assert is_palindrome("racecar") == True
    assert is_palindrome("hello") == False
    assert is_palindrome("A man a plan a canal Panama") == True
    print("✓ is_palindrome tests passed")

    print("\nTesting count_vowels:")
    assert count_vowels("hello") == 2
    assert count_vowels("AEIOU") == 5
    assert count_vowels("xyz") == 0
    print("✓ count_vowels tests passed")

    print("\n✓ All tests passed!")
