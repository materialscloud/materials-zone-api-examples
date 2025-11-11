"""
mz_operations.py

This module contains higher-level operations for working with the MaterialsZone platform,
such as creating tables, protocols, items, and uploading data.

These functions use the lower-level API helpers from `mz_api_helpers.py` to carry out
specific tasks like creating materials and experiment tables, or uploading data from Excel files.

You can use these operations in your main script to build and manage your workspace.
"""
from typing import Any

from mz_api_helpers import delete, get, patch, post


def create_parser(name: str,
                  physical_measurement: str,
                  instrument_manufacturer: str,
                  instrument_model: str,
                  supported_file_extensions: list[str],
                  configuration_columns: list[dict[str, str | int]],
                  computed_columns: list[dict[str, str | list[str]]] = [],
                  metadata_expected: bool = False,
                  footer_expected: bool = False,
                  view_type: str = 'VIEW_2D_CUSTOM_AXES',
                  description: str | None = None) -> dict[str, Any]:
    """Create a parser with values in the user's organization and return the parser details."""
    payload = {
        "name": name,
        "description": description,
        "physicalMeasurement": physical_measurement,
        "instrumentManufacturer": instrument_manufacturer,
        "instrumentModel": instrument_model,
        "enabledState": True,
        "parserConfiguration": {
            "configurationColumns": configuration_columns,
            "computedColumns": computed_columns,
            "metadataExpected": metadata_expected,
            "footerExpected": footer_expected
        },
        "viewType": view_type,
        "supportedFileExtensions": supported_file_extensions,
    }
    parser = post("/parsers", payload)
    print(f"  ✓ Created parser [{name}] with id [{parser['id']}] and code [{parser['code']}]")
    return parser


def update_parser(parser_id: str,
                  name: str | None = None,
                  description: str | None = None,
                  physical_measurement: str | None = None,
                  instrument_manufacturer: str | None = None,
                  instrument_model: str | None = None,
                  enabled_state: bool | None = None,
                  supported_file_extensions: list[str] | None = None,
                  configuration_columns: list[dict[str, str | int]] | None = None,
                  computed_columns: list[dict[str, str | list[str]]] | None = None,
                  metadata_expected: bool | None = None,
                  footer_expected: bool | None = None,
                  view_type: str | None = None) -> dict[str, Any]:
    """Update an existing parser by its id and return the parser details."""
    payload = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if physical_measurement is not None:
        payload["physicalMeasurement"] = physical_measurement
    if instrument_manufacturer is not None:
        payload["instrumentManufacturer"] = instrument_manufacturer
    if instrument_model is not None:
        payload["instrumentModel"] = instrument_model
    if enabled_state is not None:
        payload["enabledState"] = enabled_state
    if view_type is not None:
        payload["viewType"] = view_type
    if supported_file_extensions is not None:
        payload["supportedFileExtensions"] = supported_file_extensions

    if configuration_columns is not None or computed_columns is not None or \
            metadata_expected is not None or footer_expected is not None:
        parser_configuration = {}

        if configuration_columns is not None:
            parser_configuration["configurationColumns"] = configuration_columns
        if computed_columns is not None:
            parser_configuration["computedColumns"] = computed_columns
        if metadata_expected is not None:
            parser_configuration["metadataExpected"] = metadata_expected
        if footer_expected is not None:
            parser_configuration["footerExpected"] = footer_expected

        payload["parserConfiguration"] = parser_configuration

    parser = patch(f"/parsers/{parser_id}", payload)
    print(f"  ✓ Updated parser [{name}] with id [{parser_id}] and code [{parser['code']}]")
    return parser


def delete_parser(parser_id: str) -> None:
    """Delete the parser specified by parser_id"""
    delete(f"/parsers/{parser_id}")
    print(f"  ✓ Deleted parser {parser_id}")


def get_parser(parser_id: str) -> dict[str, Any]:
    """Get the details of the parser specified by parser_id"""
    parser = get(f"/parsers/{parser_id}")
    print(f"  ✓ Got details of parser with id [{parser_id}] and code [{parser['code']}]")
    return parser


def get_all_accessible_parsers() -> list[dict[str, Any]]:
    """Get the details for all parsers accessible to the user's organization"""
    all_accessible_parsers = get("/parsers")
    print(f"  ✓ Got details for all [{len(all_accessible_parsers)}] parsers accessible to the user's organization")
    return all_accessible_parsers
