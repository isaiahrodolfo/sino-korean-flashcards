import time
import requests
from requests.exceptions import ConnectionError, HTTPError

def safe_get(url, params=None, max_retries=5):
    delay = 1  # start with 1 second delay
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response
        except (ConnectionError, HTTPError) as e:
            print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise  # re-raise if out of retries
            time.sleep(delay)
            delay *= 2  # exponential backoff