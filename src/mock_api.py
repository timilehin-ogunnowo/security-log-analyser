
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


EXPECTED_TOKEN = os.getenv("API_TOKEN", "local-lab-token")

EVENTS = [
    {
        "event_id": 4625,
        "account": "TRoberts",
        "source_ip": "192.168.10.20",
        "status": "failure"
    },
    {
        "event_id": 4625,
        "account": "LabAdmin",
        "source_ip": "192.168.10.35",
        "status": "failure"
    },
    {
        "event_id": 4625,
        "account": "svc_backup",
        "source_ip": "192.168.10.35",
        "status": "failure"
    },
    {
        "event_id": 4624,
        "account": "TRoberts",
        "source_ip": "192.168.10.20",
        "status": "success"
    }
]


class MockAPIHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)

        if parsed_url.path != "/events":
            self.send_error(404, "Endpoint not found")
            return

        auth_header = self.headers.get("Authorization")

        if auth_header != f"Bearer {EXPECTED_TOKEN}":
            self.send_error(401, "Unauthorized")
            return

        page = int(params.get("page", ["1"])[0])

        # Simulate a slow API response on page 3
        if page == 3:
            time.sleep(8)

        page_size = 2
        start = (page - 1) * page_size
        end = start + page_size

        response_data = {
            "events": EVENTS[start:end],
            "next_page": page + 1 if end < len(EVENTS) else None
        }

        response_body = json.dumps(response_data).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()

        self.wfile.write(response_body)

    def log_message(self, format, *args):
        # Avoid logging request headers or credentials.
        return


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), MockAPIHandler)

    print("Mock authentication API running at http://127.0.0.1:8000")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMock API stopped.")
        server.server_close()
