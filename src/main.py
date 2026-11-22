
import argparse  # module for parsing command-line arguments
import sys
from pathlib import Path

from src.parser import (
    load_logs,
    analyse_failed_logons,
    export_json,
    export_csv,
)


def main():
    parser = argparse.ArgumentParser(
        description="Analyse failed Windows authentication events."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the JSON authentication log file."
    )

    parser.add_argument(
        "--output",
        default="output",
        help="Directory for generated reports."
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    if not input_path.is_file():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        records = load_logs(input_path)

        results, malformed_count = analyse_failed_logons(records)

        output_dir.mkdir(parents=True, exist_ok=True)

        json_path = output_dir / "failed_logons_report.json"
        csv_path = output_dir / "failed_logons_report.csv"

        export_json(results, json_path)
        export_csv(results, csv_path)

        total_failures = sum(
            result["total_failures"] for result in results
        )

        print("\nAnalysis completed successfully.")
        print(f"Records processed: {len(records)}")
        print(f"Failed logons identified: {total_failures}")
        print(f"Malformed records skipped: {malformed_count}")
        print(f"Accounts affected: {len(results)}")
        print(f"JSON report: {json_path}")
        print(f"CSV report: {csv_path}")

        return 0

    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
