
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url, max_retries=3, timeout=5):
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.timeout = timeout

        self.token = os.getenv("API_TOKEN")

        if not self.token:
            raise ValueError("API_TOKEN environment variable is missing.")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        })


    def get_page(self, page):
        """Retrieve one page with bounded retries."""
        url = f"{self.base_url}/events?page={page}"

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(
                    url,
                    timeout=self.timeout
                )

            except (requests.Timeout, requests.ConnectionError) as error:
                logger.warning(
                    "API request failed on attempt %s of %s: %s",
                    attempt,
                    self.max_retries,
                    type(error).__name__
                )

                if attempt == self.max_retries:
                    raise

                continue

            if response.status_code >= 500:
                logger.warning(
                    "API returned server error on attempt %s of %s",
                    attempt,
                    self.max_retries
                )

                if attempt == self.max_retries:
                    response.raise_for_status()

                continue

            response.raise_for_status()
            return response.json()

        raise RuntimeError("Maximum API retries exceeded.")


    def get_all_events(self):
        """Retrieve all pages from the API."""
        all_events = []
        page = 1

        while True:
            data = self.get_page(page)

            events = data.get("events", [])
            all_events.extend(events)

            next_page = data.get("next_page")

            if next_page is None:
                break

            page = next_page

        return all_events
