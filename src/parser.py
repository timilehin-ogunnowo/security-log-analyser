
import json
import csv
from collections import defaultdict
from datetime import datetime


def load_logs(file_path):
    """Load authentication events from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("Input must contain a JSON list of events.")

    return records


def analyse_failed_logons(records):
    """Validate and group failed logons by account and source IP."""
    grouped_events = defaultdict(
        lambda: {"total_failures": 0, "source_ips": defaultdict(int)}
    )

    malformed_records = 0

    for record in records:
        try:
            if not isinstance(record, dict):
                raise ValueError("Record must be an object.")

            event_id = record["event_id"]
            account = record["account"]
            source_ip = record["source_ip"]
            timestamp = record["timestamp"]
            status = record["status"]

            if type(event_id) is not int:
                raise ValueError("Event ID must be an integer.")

            if not all(
                isinstance(value, str) and value.strip()
                for value in (account, source_ip, timestamp, status)
            ):
                raise ValueError("Required fields must be non-empty strings.")

            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            if event_id != 4625:
                continue

            if status.lower() != "failure":
                continue

            grouped_events[account]["total_failures"] += 1
            grouped_events[account]["source_ips"][source_ip] += 1

        except (KeyError, TypeError, ValueError):
            malformed_records += 1

    results = []

    for account, details in sorted(grouped_events.items()):
        results.append({
            "account": account,
            "total_failures": details["total_failures"],
            "source_ips": dict(sorted(details["source_ips"].items()))
        })

    return results, malformed_records


def export_json(results, output_path):
    """Export analysis results to JSON."""
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)


def export_csv(results, output_path):
    """Export analysis results to CSV."""
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "account",
            "total_failures",
            "source_ip",
            "source_ip_failures"
        ])

        for result in results:
            for source_ip, count in result["source_ips"].items():
                writer.writerow([
                    result["account"],
                    result["total_failures"],
                    source_ip,
                    count
                ])
