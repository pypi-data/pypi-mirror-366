"""
Hello World Package

A simple package that provides greeting functionality.
"""

__version__ = "0.1.0"

def greet(name=None):
    """
    Print a greeting message.
    
    Args:
        name (str, optional): The name to greet. If None, prints "Hello, World!"
    """
    if name:
        print(f"Hello, {name}!")
    else:
        print("Hello, World!")


def get_greeting(name=None):
    """
    Return a greeting message as a string.
    
    Args:
        name (str, optional): The name to greet. If None, returns "Hello, World!"
        
    Returns:
        str: The greeting message
    """
    if name:
        return f"Hello, {name}!"
    else:
        return "Hello, World!"
