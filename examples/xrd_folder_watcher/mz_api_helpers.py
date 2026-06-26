"""
mz_api_helpers.py

Low-level helpers for the MaterialsZone REST API.
Handles authentication, request construction, and error reporting.

You do not need to modify this file. Just use the functions provided to
communicate with the API.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()  # loads MZ_API_KEY from .env if present

API_BASE_URL = "https://api.materials.zone/v2beta1"
API_KEY = os.getenv("MZ_API_KEY")
HEADERS = {"authorization": API_KEY}


def _assert_api_key():
    if not API_KEY:
        raise RuntimeError(
            "The MZ_API_KEY environment variable is not set. "
            "See the README for instructions."
        )


def _raise_for_auth(response: requests.Response):
    if response.status_code == 401:
        raise RuntimeError(
            "Authentication failed. Check that MZ_API_KEY is correct. "
            f"Server response: {response.text}"
        )


def get(endpoint: str) -> dict | list:
    """Send a GET request and return response data."""
    _assert_api_key()
    response = requests.get(f"{API_BASE_URL}{endpoint}", headers=HEADERS)
    _raise_for_auth(response)
    response.raise_for_status()
    return response.json()["data"]


def post(endpoint: str, payload: dict) -> dict:
    """Send a POST request and return the created object."""
    _assert_api_key()
    response = requests.post(f"{API_BASE_URL}{endpoint}", headers=HEADERS, json=payload)
    _raise_for_auth(response)
    response.raise_for_status()
    return response.json()["data"]


def post_with_file(endpoint: str, payload: dict, files: dict) -> dict:
    """Send a multipart POST request (for file uploads) and return the created object."""
    _assert_api_key()
    response = requests.post(f"{API_BASE_URL}{endpoint}", headers=HEADERS, data=payload, files=files)
    _raise_for_auth(response)
    response.raise_for_status()
    return response.json()["data"]


def patch(endpoint: str, payload: dict) -> dict:
    """Send a PATCH request and return the updated object."""
    _assert_api_key()
    response = requests.patch(f"{API_BASE_URL}{endpoint}", headers=HEADERS, json=payload)
    _raise_for_auth(response)
    response.raise_for_status()
    return response.json()["data"]


def delete(endpoint: str) -> None:
    """Send a DELETE request."""
    _assert_api_key()
    response = requests.delete(f"{API_BASE_URL}{endpoint}", headers=HEADERS)
    _raise_for_auth(response)
    response.raise_for_status()
