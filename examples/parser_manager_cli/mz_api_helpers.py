"""
mz_api_helpers.py

This module contains helper functions for interacting with the MaterialsZone API.
It defines how to send GET, POST, PATCH, and DELETE requests, including support for
file uploads. It also stores the base API URL, API key, and request headers.

You do not need to change anything here. Just use the functions provided to
communicate with the API.
"""

import os
import requests

API_BASE_URL = "https://api.materials.zone/v2beta1"
API_KEY = os.getenv("MZ_API_KEY")  # Set this in your environment (see README)
HEADERS = {"authorization": API_KEY}

def get(endpoint: str) -> dict | list:
    """Send a GET request to the API to fetch an object."""
    response = requests.get(f"{API_BASE_URL}{endpoint}", headers=HEADERS)
    response.raise_for_status()
    return response.json()["data"]

def post(endpoint: str, payload: dict) -> dict:
    """Send a POST request to the API to create an object."""
    response = requests.post(f"{API_BASE_URL}{endpoint}", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["data"]

def patch(endpoint: str, payload: dict) -> dict:
    """Send a PATCH request to the API to update an object."""
    response = requests.patch(f"{API_BASE_URL}{endpoint}", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["data"]

def delete(endpoint: str) -> None:
    """Send a DELETE request to the API to delete an object."""
    response = requests.delete(f"{API_BASE_URL}{endpoint}", headers=HEADERS)
    response.raise_for_status()
