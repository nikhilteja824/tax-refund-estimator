from dotenv import load_dotenv
import os
import requests
from utils.logger import logger

load_dotenv()

host = os.getenv("COMPARABLES_API_HOST", "http://localhost")
port = os.getenv("COMPARABLES_API_PORT", "8082")

COMPARABLES_API_BASE_URL = f"{host}:{port}/comp?pin="


def fetch_property_data(pin):
    """
    Calls the Comparables API, takes host and port from env variables as they are sensitive.
    Formats the response in order to be useful for wrapper API endpoint.
    """
    url = f"{COMPARABLES_API_BASE_URL}{pin}"
    logger.info(f"Requesting comparables for PIN: {pin}")

    try:
        response = requests.get(url, timeout=5)
        
        # Reusing the "detail" field from the response of comparables API
        try:
            error_body = response.json()
            api_error_message = error_body.get("detail") or error_body.get("error")
        except ValueError:
            api_error_message = None

        if response.status_code == 404:
            logger.warning(f"No property found for PIN: {pin}")
            return None, api_error_message or f"No property found for PIN: {pin}", 404

        elif response.status_code == 422:
            logger.warning(f"Invalid request format for PIN: {pin}")
            return None, f"Invalid request format", 422

        elif response.status_code != 200:
            logger.error(f"Comparables API error {response.status_code} for PIN: {pin} - {api_error_message}")
            return None, api_error_message or f"Comparables API returned {response.status_code}", 502

        logger.info(f"Successfully fetched comparables for PIN: {pin}")
        return response.json(), None, 200

    except requests.exceptions.RequestException as e:
        logger.exception(f"Error reaching Comparables API for PIN: {pin}")
        return None, f"Failed to reach Comparables API: {str(e)}", 502


def process_comparables_data(data):
    """
    Separates Target Property and its comparables
    Source of Truth: API contract mentions that first key in the response is always our target property
    """
    if not data:
        logger.warning("Empty data passed to process_comparables_data()")
        return None, []

    keys = list(data.keys())
    property_key = keys[0]
    property_ = data[property_key]
    comparables = [data[k] for k in keys[1:]]

    logger.info(f"Parsed {len(comparables)} comparables for target property key: {property_key}")
    return property_, comparables


def compute_average_assessed_value(comparables):
    """
    Computes the average assessed value of the comparable properties.
    Skips properties without 'assessed value'.
    """
    values = [c.get("assessed value") for c in comparables if "assessed value" in c]

    if not values:
        logger.warning("No valid comparables with assessed value found")
        return None

    avg = sum(values) / len(values)
    logger.info(f"Computed average assessed value from {len(values)} comparables: {avg:.2f}")

    return avg
