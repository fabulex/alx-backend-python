#!/usr/bin/env python3
"""Unit tests for utils module"""

import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Tests for access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Tests access_nested_map for valid paths."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        """Tests access_nested_map raises KeyError for invalid paths."""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(context.exception.args[0], path[-1])


class TestGetJson(unittest.TestCase):
    """Tests for get_json function"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """Tests get_json returns expected payload without HTTP calls."""
        mock_resp = Mock()
        mock_resp.json.return_value = test_payload
        mock_get.return_value = mock_resp

        result = get_json(test_url)
        self.assertEqual(result, test_payload)
        mock_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """Tests for memoize decorator"""

    def test_memoize(self):
        """Tests memoize caches method result after first call."""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(
            TestClass, 'a_method', return_value=42
        ) as mock_method:
            test_obj = TestClass()
            # Call property twice
            self.assertEqual(test_obj.a_property, 42)
            self.assertEqual(test_obj.a_property, 42)
            # Ensure method was called only once
            mock_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()
