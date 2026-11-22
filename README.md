# Security Log Analyser

A Python-based command-line security utility for analysing authentication logs, identifying failed login attempts, aggregating suspicious activity and generating structured reports.

The project also includes a local mock API for demonstrating HTTP communication, pagination, timeout handling and bounded retry behaviour.

## Features

### Authentication Log Analysis
- Processes synthetic Windows authentication events (Event IDs 4625 and 4624).
- Identifies and groups failed logon attempts by account and source IP address.
- Excludes successful authentication events.
- Validates required fields and timestamps.
- Handles malformed records without terminating the entire analysis.
- Supports empty input and invalid JSON handling.

### Report Generation
- Generates structured JSON reports.
- Generates CSV reports for further analysis.
- Preserves the original input files.
- Displays an execution summary in the terminal.

### API Client
- Communicates with a local HTTP mock API.
- Supports Bearer token authentication.
- Implements paginated data retrieval.
- Handles request timeouts and connection failures.
- Implements bounded retries for temporary failures.
- Avoids unnecessary retries for client-side HTTP errors.
- Uses environment variables for credential configuration.

### Automated Testing
- Tests authentication log parsing and aggregation.
- Tests malformed and empty input.
- Tests invalid JSON and missing files.
- Tests API request handling.
- Tests timeout, connection and server failure scenarios.
- Verifies bounded retry behaviour.

## Technology Stack

- **Language:** Python
- **HTTP Client:** Requests
- **API Server:** Python `http.server`
- **Configuration:** python-dotenv
- **Testing:** unittest, unittest.mock
- **Version Control:** Git

## Project Structure

```text
security-log-analyser/
│
├── src/
│   ├── __init__.py
│   ├── parser.py
│   ├── api_client.py
│   ├── mock_api.py
│   └── main.py
│
├── tests/
│   ├── test_parser.py
│   └── test_api_client.py
│
├── samples/
│   └── failed_logons.json
│
├── output/
│   └── .gitkeep
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

Ensure the following are installed:

- Python 3.14
- pip
- Git

Verify your installations:

```bash
python --version
pip --version
git --version
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
```

Navigate into the project directory:

```bash
cd security-log-analyser
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
.venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root.

Copy the configuration template:

```powershell
Copy-Item .env.example .env
```

Configure the API token:

```env
API_TOKEN=local-lab-token
```

The mock API uses `local-lab-token` as its default local development token.

**Security Notes:**
- Never commit the `.env` file.
- Keep credentials out of source code.
- Do not print authentication tokens in application logs.
- Use secure, unique credentials outside this isolated local lab.

## Running the Application

### 1. Analyse Authentication Logs

Run the command-line utility:

```bash
python -m src.main --input samples/failed_logons.json
```

Specify a custom output directory if required:

```bash
python -m src.main --input samples/failed_logons.json --output output
```

### 2. Generated Reports

After successful execution, the application generates:

```text
output/
├── failed_logons_report.json
└── failed_logons_report.csv
```

**Expected Terminal Output:**

```text
Analysis completed successfully.
Records processed: 5
Failed logons identified: 4
Malformed records skipped: 0
Accounts affected: 3
JSON report: output\failed_logons_report.json
CSV report: output\failed_logons_report.csv
```

### 3. Running the Mock API Server

Open a separate terminal from the project root.

Activate the virtual environment if necessary:

```powershell
.venv\Scripts\Activate.ps1
```

Start the local API server:

```bash
python -m src.mock_api
```

Expected output:

```text
Mock authentication API running at http://127.0.0.1:8000
```

The API runs locally on port `8000`.

### 4. Test API Communication

Keep the mock API server running.

Open another terminal and execute:

```bash
python -c "from src.api_client import APIClient; client = APIClient('http://127.0.0.1:8000'); events = client.get_all_events(); print(f'Retrieved {len(events)} events'); print(events)"
```

Expected output:

```text
Retrieved 4 events
```

The client retrieves authentication events across multiple API pages.

## Running Automated Tests

The project uses Python's built-in `unittest` framework.

From the project root, run:

```bash
python -m unittest discover -s tests -v
```

The test suite covers:

| Test Area | Scenarios |
|---|---|
| Log Parser | Failed logon detection and aggregation |
| Authentication | Successful logon exclusion |
| Input Validation | Empty input and malformed records |
| File Handling | Invalid JSON, incorrect JSON structure and missing files |
| API Client | Successful requests |
| API Reliability | Timeout and connection failures |
| Retry Behaviour | Bounded retries and server errors |
| HTTP Errors | Client errors without unnecessary retries |

**Expected Test Summary:**

```text
Ran 13 tests

OK
```

## API Behaviour

The local mock API simulates authentication event retrieval.

| Feature | Behaviour |
|---|---|
| Base URL | `http://127.0.0.1:8000` |
| Endpoint | `/events` |
| Authentication | Bearer token |
| Pagination | Two events per page |
| Timeout Simulation | Delayed response |
| Retry Limit | Three attempts |
| HTTP 401 | Unauthorized |
| HTTP 404 | Endpoint not found |
| HTTP 5xx | Server error |

## Error Handling

The utility is designed to handle common operational failures, including:

- Missing input files.
- Invalid JSON data.
- Incorrect input structures.
- Missing or malformed authentication records.
- API connection failures.
- Request timeouts.
- HTTP client and server errors.

Malformed records are skipped and counted, while unrecoverable input and API errors are reported clearly.

## Security Considerations

- Synthetic authentication records are used for testing.
- API credentials are configured through environment variables.
- `.env` is excluded from version control.
- Generated reports are excluded from version control.
- API failure logs record error types without exposing credentials.
- The mock API binds to `127.0.0.1` and is intended for local development and testing.

## Future Improvements

- Support for parsing native Windows Security Event exports.
- IP address validation and additional event enrichment.
- Detection of repeated failed logons and potential brute-force activity.
- Additional structured logging and reporting.
- Integration with external security monitoring platforms.

## Author

**Timilehin Ogunnowo**

Security Engineering | Python | Application Security

