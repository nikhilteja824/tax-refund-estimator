import os
import requests
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("COMPARABLES_API_HOST", "http://localhost")
port = os.getenv("COMPARABLES_API_PORT", "8082")

COMPARABLES_API_BASE_URL = f"{host}:{port}/comp?pin="

def fetch_property_data(pin):
    try:
        url = f"{COMPARABLES_API_BASE_URL}{pin}"
        response = requests.get(url, timeout=5)

        # Reusing the "detail" field from the response of comparables API
        try:
            error_body = response.json()
            api_error_message = error_body.get("detail") or error_body.get("error")
        except ValueError:
            api_error_message = None

        if response.status_code == 404:
            return None, api_error_message or f"No property found for PIN: {pin}", 404
        elif response.status_code == 422:
            return None, f"Invalid request format", 422
        elif response.status_code != 200:
            return None, api_error_message or f"Comparables API returned {response.status_code}", 502

        return response.json(), None, 200

    except requests.exceptions.RequestException as e:
        return None, f"Failed to reach Comparables API: {str(e)}", 502