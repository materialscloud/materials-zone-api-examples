"""
mz_operations.py

Higher-level operations for the XRD folder watcher example.

Wraps the low-level API helpers with domain-specific logic: creating the
table structure, finding and creating phase items, uploading XRD composition
data as formulation values, and attaching the raw CSV file to a material item.
"""

from __future__ import annotations

from pathlib import Path
from mz_api_helpers import get, post, post_with_file, patch


def get_folder_id_by_name(folder_title: str) -> str:
    """Return the ID of the folder matching the given title, or raise if not found."""
    folders = get("/folders")
    for folder in folders:
        if folder["title"] == folder_title:
            return folder["id"]
    raise ValueError(f"Folder '{folder_title}' not found. Create it in MaterialsZone first.")


def get_tables_in_folder(folder_id: str) -> list:
    """Return all tables in a folder."""
    return [t for t in get("/tables") if t.get("folderId") == folder_id]


def create_table(folder_id: str, title: str) -> str:
    """Create a table in a folder and return its ID."""
    table = post("/tables", {"title": title, "description": title, "folderId": folder_id})
    print(f"  ✓ Created table '{title}' (id: {table['id']})")
    return table["id"]


def create_protocol(table_id: str, title: str) -> str:
    """Create a protocol in a table and return its ID."""
    protocol = post(f"/tables/{table_id}/protocols", {"title": title})
    print(f"  ✓ Created protocol '{title}' (id: {protocol['id']})")
    return protocol["id"]


def create_text_parameter(protocol_id: str, title: str) -> str:
    """Create a TEXT parameter under a protocol and return its ID."""
    parameter = post(f"/protocols/{protocol_id}/parameters", {"title": title, "valueType": "TEXT"})
    print(f"  ✓ Created parameter '{title}' (id: {parameter['id']})")
    return parameter["id"]


def create_quantity_parameter(protocol_id: str, title: str, unit: str = None) -> str:
    """Create a QUANTITY parameter under a protocol and return its ID."""
    payload = {"title": title, "valueType": "QUANTITY"}
    if unit:
        payload["unit"] = unit
    parameter = post(f"/protocols/{protocol_id}/parameters", payload)
    print(f"  ✓ Created parameter '{title}' (id: {parameter['id']})")
    return parameter["id"]


def create_formulation_protocol(table_id: str, title: str, title_table_ids: list) -> str:
    """Create a formulation protocol linking to a lookup table and return its ID."""
    payload = {"title": title, "unit": "Wt%", "titleTableIds": title_table_ids}
    fp = post(f"/tables/{table_id}/formulation-protocols", payload)
    print(f"  ✓ Created formulation protocol '{title}' (id: {fp['id']})")
    return fp["id"]


def create_item(table_id: str, title: str, values: list = None) -> dict:
    """Create an item in a table and return the item dict."""
    item = post(f"/tables/{table_id}/items", {"title": title, "values": values or []})
    print(f"  ✓ Created item '{title}' (id: {item['id']})")
    return item


def update_item(item_id: str, values: list) -> dict:
    """Update an existing item with new values and return the updated item."""
    return patch(f"/items/{item_id}", {"values": values})


def get_all_items(table_id: str) -> list:
    """Return all items in a table, following pagination."""
    items = []
    cursor = None
    while True:
        endpoint = f"/tables/{table_id}/items?pageSize=100"
        if cursor:
            endpoint += f"&cursor={cursor}"
        result = get(endpoint)
        items.extend(result["data"])
        if not result["pagination"]["hasNextPage"]:
            break
        cursor = result["pagination"]["endCursor"]
    return items


def get_item_by_title(table_id: str, title: str) -> dict | None:
    """Return the first item with the given title, or None if not found."""
    for item in get_all_items(table_id):
        if item.get("title") == title:
            return item
    return None


def get_parameter_id(table_id: str, protocol_title: str, parameter_title: str) -> str:
    """Return the ID of a named parameter within a named protocol in a table."""
    table = get(f"/tables/{table_id}")
    for protocol in table.get("protocols", []):
        if protocol.get("type") == "PROTOCOL" and protocol.get("title") == protocol_title:
            for param in protocol.get("parameters", []):
                if param.get("title") == parameter_title:
                    return param["id"]
    raise ValueError(
        f"Parameter '{parameter_title}' not found in protocol '{protocol_title}' "
        f"in table {table_id}."
    )


def get_formulation_protocol_id(table_id: str, title: str) -> str:
    """Return the ID of the named formulation protocol in a table.

    The full table structure — including all protocols and formulation protocols —
    is returned by GET /tables/{tableId}. There is no separate listing endpoint.
    """
    table = get(f"/tables/{table_id}")
    for protocol in table.get("protocols", []):
        if protocol.get("type") == "FORMULATION" and protocol.get("title") == title:
            return protocol["id"]
    raise ValueError(f"Formulation protocol '{title}' not found in table {table_id}.")


def ensure_phase_item(phases_table_id: str, phase_name: str,
                      pdf_parameter_id: str = None, pdf_num: str = "",
                      formula_parameter_id: str = None, formula: str = "") -> str:
    """Return the phase item ID for phase_name, creating it in the XRD Phases table if needed.

    If the phase exists but is missing formula or PDF-# (e.g. pre-populated by setup.py
    without those values), the missing fields are patched onto the existing item.
    If the phase is new, it is created with all provided values from the start.
    """
    item = get_item_by_title(phases_table_id, phase_name)
    if item:
        updates = []
        existing_values = item.get("values") or []
        for param_id, value in [(pdf_parameter_id, pdf_num), (formula_parameter_id, formula)]:
            if param_id and value:
                current = next(
                    (v.get("value") for v in existing_values if v.get("parameterId") == param_id),
                    None,
                )
                if current != value:
                    updates.append({"parameterId": param_id, "value": value})
        if updates:
            update_item(item["id"], updates)
        return item["id"]
    values = []
    for param_id, value in [(pdf_parameter_id, pdf_num), (formula_parameter_id, formula)]:
        if param_id and value:
            values.append({"parameterId": param_id, "value": value})
    new_item = create_item(phases_table_id, phase_name, values)
    return new_item["id"]


def clear_composition(item_id: str, formulation_protocol_id: str) -> None:
    """Clear all existing XRD composition values on an item.

    Called before re-uploading an updated file to avoid duplicate entries.
    Individual formulation entries are cleared by patching their value to null.
    """
    item = get(f"/items/{item_id}")
    entries_to_clear = [
        {
            "formulationProtocolId": v["formulationProtocolId"],
            "formulationItemId": v["formulationItemId"],
            "value": None,
        }
        for v in (item.get("values") or [])
        if v.get("formulationProtocolId") == formulation_protocol_id
    ]
    if entries_to_clear:
        patch(f"/items/{item_id}", {"values": entries_to_clear})


def upload_composition(item_id: str, formulation_protocol_id: str, phase_entries: list) -> None:
    """Upload phase composition values to a material item.

    phase_entries: list of {"phase_item_id": str, "wt_pct": float}
    """
    values = [
        {
            "formulationProtocolId": formulation_protocol_id,
            "formulationItemId": entry["phase_item_id"],
            "value": str(entry["wt_pct"]),
        }
        for entry in phase_entries
    ]
    patch(f"/items/{item_id}", {"values": values})


def upload_file(item_id: str, file_path) -> None:
    """Attach a CSV file as a measurement record on a material item."""
    file_path = Path(file_path)
    payload = {"title": file_path.name}
    with open(file_path, "rb") as f:
        post_with_file(
            f"/items/{item_id}/measurements",
            payload,
            {"rawFile": (file_path.name, f, "text/csv")},
        )
    print(f"  ✓ Attached '{file_path.name}' to item {item_id}")
