


import unittest
import json

import tempfile
from pathlib import Path
from src.parser import load_logs

from src.parser import analyse_failed_logons


class TestAuthenticationParser(unittest.TestCase):

    def setUp(self):
        self.valid_event = {
            "event_id": 4625,
            "timestamp": "2026-11-22T08:15:00Z",
            "account": "TRoberts",
            "source_ip": "192.168.10.20",
            "status": "failure"
        }

    def test_failed_logon_is_counted(self):
        results, malformed = analyse_failed_logons(
            [self.valid_event]
        )

        self.assertEqual(results[0]["account"], "TRoberts")
        self.assertEqual(results[0]["total_failures"], 1)
        self.assertEqual(malformed, 0)

    def test_successful_logon_is_excluded(self):
        event = self.valid_event.copy()
        event["event_id"] = 4624
        event["status"] = "success"

        results, malformed = analyse_failed_logons([event])

        self.assertEqual(results, [])
        self.assertEqual(malformed, 0)

    def test_empty_input(self):
        results, malformed = analyse_failed_logons([])

        self.assertEqual(results, [])
        self.assertEqual(malformed, 0)

    def test_malformed_record_is_skipped(self):
        malformed_event = {
            "event_id": 4625,
            "timestamp": "2026-11-22T08:15:00Z",
            "source_ip": "192.168.10.20",
            "status": "failure"
        }

        results, malformed = analyse_failed_logons(
            [self.valid_event, malformed_event]
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(malformed, 1)

    def test_non_object_record_is_skipped(self):
        results, malformed = analyse_failed_logons(
            [self.valid_event, "invalid record"]
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(malformed, 1)

    
    def test_invalid_json_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "invalid.json"
            file_path.write_text("{invalid json}", encoding="utf-8")

            with self.assertRaises(json.JSONDecodeError):
                load_logs(file_path)

    def test_json_object_instead_of_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "wrong_format.json"
            file_path.write_text('{"account": "TRoberts"}', encoding="utf-8")

            with self.assertRaises(ValueError):
                load_logs(file_path)

    def test_missing_input_file(self):
        with self.assertRaises(FileNotFoundError):
            load_logs("samples/nonexistent.json")



if __name__ == "__main__":
    unittest.main()
