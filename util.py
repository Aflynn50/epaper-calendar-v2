import requests
import logging

def internet_available() -> bool:
    for attempt in range(3):
        try:
            requests.get("https://google.com", timeout=5)
            return True
        except (requests.ConnectionError, requests.Timeout) as e:
            logging.error(e)
        return False
