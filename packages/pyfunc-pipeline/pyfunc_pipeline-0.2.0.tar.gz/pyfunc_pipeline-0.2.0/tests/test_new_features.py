#!/usr/bin/env python3
"""Test script for the new PyFunc features."""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyfunc import pipe, _, Pipeline

class TestNewFeatures(unittest.TestCase):

    def test_basic_functionality(self):
        """Test basic pipe functionality."""
        # Test pipe as main entry point
        result = pipe([1, 2, 3, 4]).filter(_ > 2).map(_ * 10).to_list()
        self.assertEqual(result, [30, 40])
        
        # Test scalar operations
        result = pipe(10).then(_ * 2).then(str).get()
        self.assertEqual(result, "20")

    def test_string_methods(self):
        """Test string manipulation methods."""
        # Test explode
        result = pipe("hello").explode().to_list()
        self.assertEqual(result, ['h', 'e', 'l', 'l', 'o'])
        
        result = pipe("hello world").explode(" ").to_list()
        self.assertEqual(result, ['hello', 'world'])
        
        # Test implode
        result = pipe(['h', 'e', 'l', 'l', 'o']).implode().get()
        self.assertEqual(result, "hello")
        
        result = pipe(['hello', 'world']).implode(" ").get()
        self.assertEqual(result, "hello world")
        
        # Test surround
        result = pipe("hello").surround("<", ">").get()
        self.assertEqual(result, "<hello>")
        
        # Test template_fill
        result = pipe("Hello {name}!").template_fill({"name": "World"}).get()
        self.assertEqual(result, "Hello World!")

    def test_dictionary_methods(self):
        """Test dictionary manipulation methods."""
        data = {"a": 1, "b": 2, "c": 3}
        
        # Test with_items
        result = pipe(data).with_items().to_list()
        self.assertEqual(set(result), {('a', 1), ('b', 2), ('c', 3)})
        
        # Test map_values
        result = pipe(data).map_values(_ * 10).get()
        self.assertEqual(result, {"a": 10, "b": 20, "c": 30})
        
        # Test map_keys
        result = pipe(data).map_keys(_.upper()).get()
        self.assertEqual(result, {"A": 1, "B": 2, "C": 3})

    def test_side_effects(self):
        """Test side effect methods."""
        captured = []
        
        # Test do/tap
        result = pipe([1, 2, 3]).do(lambda x: captured.append(f"Processing: {x}")).map(_ * 2).to_list()
        self.assertEqual(result, [2, 4, 6])
        self.assertEqual(len(captured), 1)
        
        # Test debug (just make sure it doesn't crash)
        result = pipe([1, 2, 3]).debug("Test").map(_ * 2).to_list()
        self.assertEqual(result, [2, 4, 6])

    def test_composition(self):
        """Test function composition."""
        # Test placeholder composition
        double = _ * 2
        square = _ ** 2
        composed = double >> square  # square(double(x))
        
        result = pipe(3).apply(composed).get()
        self.assertEqual(result, 36)
        
        # Test reverse composition
        composed_reverse = square << double  # square(double(x))
        result = pipe(3).apply(composed_reverse).get()
        self.assertEqual(result, 36)

    def test_complex_pipeline(self):
        """Test a complex real-world pipeline."""
        # Process a list of user data
        users = [
            {"name": "  Alice  ", "age": 30, "scores": [85, 92, 78]},
            {"name": "BOB", "age": 25, "scores": [90, 88, 95]},
            {"name": "charlie", "age": 35, "scores": [75, 80, 85]},
        ]
        
        result = (pipe(users)
                  .map(lambda user: {
                      "name": pipe(user["name"]).apply(_.strip().title()).get(),
                      "age": user["age"],
                      "avg_score": pipe(user["scores"]).sum().get() / len(user["scores"])
                  })
                  .filter(lambda user: user["avg_score"] > 80)
                  .sort(key=lambda user: user["avg_score"], reverse=True)
                  .to_list())
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Bob")
        self.assertEqual(result[1]["name"], "Alice")

    def test_group_by(self):
        """Test group_by functionality."""
        data = [
            {"name": "Alice", "department": "Engineering"},
            {"name": "Bob", "department": "Sales"},
            {"name": "Charlie", "department": "Engineering"},
            {"name": "Diana", "department": "Sales"},
        ]
        
        result = pipe(data).group_by(_["department"]).get()
        
        self.assertIn("Engineering", result)
        self.assertIn("Sales", result)
        self.assertEqual(len(result["Engineering"]), 2)
        self.assertEqual(len(result["Sales"]), 2)

    def test_to_list_method(self):
        """Test the to_list method."""
        # Test with generator
        result = pipe([1, 2, 3]).map(_ * 2).to_list()
        self.assertEqual(result, [2, 4, 6])
        
        # Test with scalar
        result = pipe(42).to_list()
        self.assertEqual(result, [42])

if __name__ == "__main__":
    unittest.main()