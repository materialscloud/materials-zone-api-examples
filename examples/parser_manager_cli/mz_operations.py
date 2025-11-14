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


def create_parser(parser_payload: dict[str, Any]) -> dict[str, Any]:
    """Create a parser with the provided payload and return the parser details."""
    parser = post("/parsers", parser_payload)
    print(f"  ✓ Created parser [{parser_payload.get('name', 'N/A')}] with id [{parser['id']}] and code [{parser['code']}]")
    return parser


def update_parser(parser_id: str, parser_payload: dict[str, Any]) -> dict[str, Any]:
    """Update an existing parser by its id using the provided payload and return the parser details."""
    parser = patch(f"/parsers/{parser_id}", parser_payload)
    print(f"  ✓ Updated parser [{parser_payload.get('name', 'N/A')}] with id [{parser_id}] and code [{parser['code']}]")
    return parser


def delete_parser(parser_id: str) -> None:
    """Delete the parser specified by parser_id"""
    delete(f"/parsers/{parser_id}")
    print(f"  ✓ Deleted parser {parser_id}")


def get_all_parsers() -> list[dict[str, Any]]:
    """Get the details for all parsers accessible to the user's organization"""
    all_accessible_parsers = get("/parsers")
    print(f"  ✓ Got details for all [{len(all_accessible_parsers)}] parsers accessible to the user's organization")
    return all_accessible_parsers
