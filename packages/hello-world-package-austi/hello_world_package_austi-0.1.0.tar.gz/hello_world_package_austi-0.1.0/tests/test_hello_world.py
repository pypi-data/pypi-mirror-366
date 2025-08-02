"""
Tests for the hello world package.
"""

import unittest
from unittest.mock import patch
import io
import sys
from hello_world import greet, get_greeting


class TestHelloWorld(unittest.TestCase):
    
    def test_get_greeting_no_name(self):
        """Test greeting without a name."""
        result = get_greeting()
        self.assertEqual(result, "Hello, World!")
    
    def test_get_greeting_with_name(self):
        """Test greeting with a name."""
        result = get_greeting("Alice")
        self.assertEqual(result, "Hello, Alice!")
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_greet_no_name(self, mock_stdout):
        """Test greet function without a name."""
        greet()
        self.assertEqual(mock_stdout.getvalue(), "Hello, World!\n")
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_greet_with_name(self, mock_stdout):
        """Test greet function with a name."""
        greet("Bob")
        self.assertEqual(mock_stdout.getvalue(), "Hello, Bob!\n")


if __name__ == "__main__":
    unittest.main()
