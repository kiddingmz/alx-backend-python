#!/usr/bin/env python3
"""Parameterize a unit test"""
from typing import Any, Dict
import unittest
from parameterized import parameterized
import requests
from utils import access_nested_map, get_json, memoize
from unittest.mock import Mock, patch


class TestAccessNestedMap(unittest.TestCase):
    """Access a nested map"""

    @parameterized.expand(
        [
            ({"a": 1}, ("a",), 1),
            ({"a": {"b": 2}}, ("a",), {"b": 2}),
            ({"a": {"b": 2}}, ("a", "b"), 2),
        ]
    )
    def test_access_nested_map(self, nested_map, path, expected):
        """Ensure that this method returns a value from the nested map given"""
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)

    @parameterized.expand(
        [
            ({}, ("a",), "a"),
            ({"a": 1}, ("a", "b"), "b"),
        ]
    )
    def test_access_nested_map_exception(self, nested_map, path, expected):
        """Test that a `KeyError` is raised"""
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)

        message = str(cm.exception)
        self.assertEqual(message[1:-1], expected)


class TestGetJson(unittest.TestCase):
    """Mock HTTP calls"""

    @parameterized.expand(
        [
            ("http://example.com", {"payload": True}),
            ("http://holberton.io", {"payload": False}),
        ]
    )
    def test_get_json(
        self, test_url: str, test_payload: Dict[str, Any]
    ) -> None:
        """Test that `utils.get_json` returns the expected result"""
        mock_get = Mock()
        mock_get.return_value.json.return_value = test_payload
        requests.get = mock_get
        result = get_json(test_url)
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test for memoization"""

    def test_memoize(self):
        """Test that function return value is memoized"""

        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, 'a_method') as mock_a_method:
            mock_a_method.return_value = 30
            foo = TestClass()
            self.assertEqual(foo.a_property, 30)
            self.assertEqual(foo.a_property, 30)

        mock_a_method.assert_called_once()
