"""
mz_operations.py

This module contains higher-level operations for working with the MaterialsZone platform,
such as creating tables, protocols, items, and uploading data.

These functions use the lower-level API helpers from `mz_api_helpers.py` to carry out
specific tasks like creating materials and experiment tables, or uploading data from Excel files.

You can use these operations in your main script to build and manage your workspace.
"""

from mz_api_helpers import get, post, post_with_file, patch, delete

def get_folder_id_by_name(folder_title: str) -> str:
    """Return the ID of a folder matching the given title."""
    folders = get("/folders")
    for folder in folders:
        if folder["title"] == folder_title:
            print(f"  ✓ Found folder {folder_title} with id {folder['id']}")
            return folder["id"]
    raise ValueError("Folder not found")

def get_tables_in_folder(folder_id: str) -> list[dict] | None:
    """Return a list of tables within the specified folder ID."""
    all_tables = get("/tables")
    tables_in_folder = [table for table in all_tables if table["folderId"] == folder_id]
    print(f"  ✓ Found {len(tables_in_folder)} tables in folder {folder_id}")
    return tables_in_folder

def create_table(folder_id: str, title: str) -> str:
    """Create a table in a folder and return its ID."""
    payload = {"title": title, "description": title, "folderId": folder_id}
    table_id = post("/tables", payload)["id"]
    print(f"  ✓ Created table {title} with id {table_id}")
    return table_id

def delete_table(table_id: str) -> None:
    """Delete the specified table by ID."""
    delete(f"/tables/{table_id}")
    print(f"  ✓ Deleted table {table_id}")

def create_protocol(table_id: str, title: str) -> str:
    """Create a protocol in a table and return its ID."""
    payload = {"title": title}
    protocol_id = post(f"/tables/{table_id}/protocols", payload)["id"]
    print(f"  ✓ Created protocol {title} with id {protocol_id}")
    return protocol_id

def create_formulation_protocol(table_id: str, title: str, title_table_ids: list[str]) -> str:
    """Create a formulation protocol and return its ID."""
    payload = {"title": title, "unit": "%", "titleTableIds": title_table_ids}
    formulation_protocol_id = post(f"/tables/{table_id}/formulation-protocols", payload)["id"]
    print(f"  ✓ Created formation protocol {title} with id {formulation_protocol_id}")
    return formulation_protocol_id

def create_parameter(protocol_id: str, title: str, unit: str=None) -> str:
    """Create a parameter under a protocol and return its ID."""
    payload = {"title": title, "valueType": "QUANTITY"}
    if unit:
        payload["unit"] = unit
    parameter_id = post(f"/protocols/{protocol_id}/parameters", payload)["id"]
    print(f"  ✓ Created parameter {title} with id {parameter_id}")
    return parameter_id

def create_protocols_and_parameters(table_id: str, protocols: list[dict]) -> dict[str, str]:
    """Create protocols and parameters in a table and return a map from column names to parameter IDs."""
    col_param_map = {}
    for protocol in protocols:
        if protocol["type"] == "protocol":
            protocol_id = create_protocol(table_id, protocol["title"])
            protocol["id"] = protocol_id
            for parameter in protocol["parameters"]:
                col_param_map[parameter["column"]] = create_parameter(protocol_id, parameter["title"],
                                                                      parameter["unit"])
        elif protocol["type"] == "formulation":
            protocol_id = create_formulation_protocol(table_id, protocol["title"], protocol["titleTableIds"])
            protocol["id"] = protocol_id

    return col_param_map

def create_item(table_id: str, title: str, values: list[dict]) -> dict:
    """Create an item with values in a table and return the item details."""
    payload = {"title": title, "values": values}
    item = post(f"/tables/{table_id}/items", payload)
    print(f"  ✓ Created item {title} with id {item['id']}")
    return item

def update_item(item_id: str, values: list[dict]) -> dict:
    """Update an existing item with new values and return the updated item."""
    payload = {"values": values}
    item = patch(f"/items/{item_id}", payload)
    print(f"  ✓ Updated item {item['title']} with id {item['id']}")
    return item

def create_measurement(item_id: str, title: str, parser_code: str, file: tuple) -> dict:
    """Upload a measurement file to an item and return the measurement details."""
    payload = {"title": title, "parserConfigurationCode": parser_code}
    files = {"rawFile": file}
    measurement = post_with_file(f"/items/{item_id}/measurements", payload, files)
    print(f"  ✓ Created measurement {title} in item with id {item_id}")
    return measurement
