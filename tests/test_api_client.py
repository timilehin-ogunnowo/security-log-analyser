
import os
import unittest
from unittest.mock import patch, Mock

import requests

from src.api_client import APIClient


class TestAPIClient(unittest.TestCase):

    def setUp(self):
        self.env_patcher = patch.dict(
            os.environ,
            {"API_TOKEN": "test-token"}
        )
        self.env_patcher.start()

        self.client = APIClient(
            "http://127.0.0.1:8000",
            max_retries=3,
            timeout=1
        )

    def tearDown(self):
        self.client.session.close()
        self.env_patcher.stop()

    @patch("src.api_client.requests.Session.get")
    def test_successful_request(self, mock_get):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "events": [{"account": "TRoberts"}],
            "next_page": None
        }
        mock_get.return_value = response

        result = self.client.get_page(1)

        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(mock_get.call_count, 1)

    @patch("src.api_client.requests.Session.get")
    def test_timeout_retries_are_bounded(self, mock_get):
        mock_get.side_effect = requests.Timeout("Request timed out")

        with self.assertRaises(requests.Timeout):
            self.client.get_page(1)

        self.assertEqual(mock_get.call_count, 3)

    @patch("src.api_client.requests.Session.get")
    def test_connection_error_retries_are_bounded(self, mock_get):
        mock_get.side_effect = requests.ConnectionError(
            "Connection unavailable"
        )

        with self.assertRaises(requests.ConnectionError):
            self.client.get_page(1)

        self.assertEqual(mock_get.call_count, 3)

    @patch("src.api_client.requests.Session.get")
    def test_server_error_retries_are_bounded(self, mock_get):
        response = Mock()
        response.status_code = 503
        response.raise_for_status.side_effect = requests.HTTPError(
            "503 Server Error"
        )
        mock_get.return_value = response

        with self.assertRaises(requests.HTTPError):
            self.client.get_page(1)

        self.assertEqual(mock_get.call_count, 3)

    @patch("src.api_client.requests.Session.get")
    def test_client_error_fails_without_retry(self, mock_get):
        response = Mock()
        response.status_code = 401
        response.raise_for_status.side_effect = requests.HTTPError(
            "401 Unauthorized"
        )
        mock_get.return_value = response

        with self.assertRaises(requests.HTTPError):
            self.client.get_page(1)

        self.assertEqual(mock_get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
