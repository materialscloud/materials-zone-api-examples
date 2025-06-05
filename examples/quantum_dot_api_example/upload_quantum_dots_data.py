import os
import pandas as pd
import requests
import glob
import numpy as np
from scipy.signal import find_peaks

# --- Configuration ---
API_BASE_URL = "https://api.materials.zone/v2beta1"
API_KEY = os.getenv("MZ_API_KEY")  # Set this in your environment (see README)
EXCEL_PATH = "quantum_dots_example.xlsx"
MEASUREMENT_FOLDER = "measurements"  # Folder containing measurement CSV files
FOLDER_TITLE = "Quantum Dot Example" # Replace with the title of the folder you created
HEADERS = {"authorization": API_KEY}

# --- API Helper Functions ---
def get(endpoint: str) -> dict:
    """Send a GET request to the API to fetch an object."""
    response = requests.get(f"{API_BASE_URL}{endpoint}", headers=HEADERS)
    response.raise_for_status()
    return response.json()["data"]

def post(endpoint: str, payload: dict) -> dict:
    """Send a POST request to the API to create an object."""
    response = requests.post(f"{API_BASE_URL}{endpoint}", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["data"]

def post_with_file(endpoint: str, payload: dict, files: dict) -> dict:
    """Send a multipart POST request to the API to create an object that requires uploading a file."""
    response = requests.post(f"{API_BASE_URL}{endpoint}", headers=HEADERS, data=payload, files=files)
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

# --- MZ Object Operations ---
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

# --- Helper Functions ---
def delete_existing_tables(folder_id: str, materials_table_title, experiments_table_title):
    """Delete tables with given titles from the specified folder if they exist."""
    tables = get_tables_in_folder(folder_id)

    materials_table_id = next((table["id"] for table in tables if table["title"] == materials_table_title), None)
    experiments_table_id = next((table["id"] for table in tables if table["title"] == experiments_table_title), None)

    if experiments_table_id:
        delete_table(experiments_table_id)
    if materials_table_id:
        delete_table(materials_table_id)

def create_protocols(table_id: str, protocols: list[dict]) -> dict[str, str]:
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

# --- Tables, Protocols and Parameters Creation ---
def create_materials_table(folder_id: str, materials_table_title: str) -> tuple[str, dict]:
    """Create the Materials table with predefined protocols and return its ID and column-to-parameter map."""
    materials_table_id = create_table(folder_id, materials_table_title)
    materials_table_protocols = [
        {
            "title": "Properties",
            "type": "protocol",
            "parameters": [
                {
                    "title": "Band Gap",
                    "unit": "eV",
                    "column": "Band Gap (eV)"
                },
                {
                    "title": "Size",
                    "unit": "nm",
                    "column": "Size (nm)"
                },
                {
                    "title": "Quantum Yield",
                    "unit": "%",
                    "column": "Quantum Yield (%)"
                }
            ]
        }
    ]
    mat_col_param_map = create_protocols(materials_table_id, materials_table_protocols)

    return materials_table_id, mat_col_param_map

def create_experiments_table(folder_id: str, experiments_table_title: str,
                             materials_table_id: str) -> tuple[str, dict, str]:
    """Create the experiments table and return its ID, column-to-parameter map, and formulation protocol ID."""
    table_id = create_table(folder_id, experiments_table_title)
    protocols = [
        {
            "title": "Formulation",
            "type": "formulation",
            "unit": "%",
            "titleTableIds": [materials_table_id]
        },
        {
            "title": "Processing Parameters",
            "type": "protocol",
            "parameters": [
                {
                    "title": "Spin Speed",
                    "unit": "rpm",
                    "column": "Spin Speed (rpm)"
                },
                {
                    "title": "Annealing Temp",
                    "unit": "C",
                    "column": "Annealing Temp (C)"
                },
                {
                    "title": "Annealing Time",
                    "unit": "min",
                    "column": "Annealing Time (min)"
                }
            ]
        },
        {
            "title": "Measured Properties",
            "type": "protocol",
            "parameters": [
                {
                    "title": "Photoluminescence",
                    "unit": "a.u.",
                    "column": "Photoluminescence (a.u.)"
                },
                {
                    "title": "Conductivity",
                    "unit": "S/m",
                    "column": "Conductivity (S/m)"
                },
                {
                    "title": "Quantum Efficiency",
                    "unit": "%",
                    "column": "Quantum Efficiency (%)"
                },
                {
                    "title": "Peak Wavelength",
                    "unit": "nm",
                    "column": "Peak Wavelength (nm)"
                }
            ]
        }
    ]
    exp_col_param_map = create_protocols(table_id, protocols)
    formulation_protocol_id = [protocol["id"] for protocol in protocols if protocol["title"] == "Formulation"][0]

    return table_id, exp_col_param_map, formulation_protocol_id

# --- Upload Items ---
def upload_materials(materials_table_id: str, mat_col_param_map: dict[str, str],
                     df_materials: pd.DataFrame) -> dict[str, str]:
    """Upload material items from a DataFrame and return a map from titles to item IDs."""
    materials_ids_map = {}
    for _, row in df_materials.iterrows():
        values = [
            {"parameterId": mat_col_param_map[col], "value": str(row[col])} for col in mat_col_param_map
        ]
        item = create_item(materials_table_id, row["Name"], values)
        materials_ids_map[item["title"]] = item["id"]

    return materials_ids_map

def upload_experiments(experiments_table_id: str, exp_col_param_map: dict[str, str], materials_ids_map: dict[str, str],
                       formulation_protocol_id: str, df_experiments: pd.DataFrame) -> dict[str, str]:
    """Upload experiment items from a DataFrame and return a map from titles to item IDs."""
    experiments_ids_map = {}
    for _, row in df_experiments.iterrows():
        values = []
        for col, val in row.items():
            if col in exp_col_param_map:
                values.append({
                    "parameterId": exp_col_param_map[col],
                    "value": str(val)
                })
            elif col in materials_ids_map and val:
                values.append({
                    "formulationProtocolId": formulation_protocol_id,
                    "formulationItemId": materials_ids_map[col],
                    "value": str(val)
                })

        item = create_item(experiments_table_id, row["Experiment ID"], values)
        experiments_ids_map[item["title"]] = item["id"]

    return experiments_ids_map

# --- Analysis and Measurement Upload ---
def find_emission_spectrum_peak_wavelength(file_path: str) -> float | None:
    """Return the peak wavelength from an emission spectrum CSV file, or None if not found."""
    df = pd.read_csv(file_path)
    x = df.iloc[:, 0].values
    y = df.iloc[:, 1].values

    # Simple peak detection
    peaks, _ = find_peaks(y)
    peak_x = x[peaks[np.argmax(y[peaks])]] if len(peaks) > 0 else None

    return peak_x

def upload_emission_spectrum_measurements(exp_col_param_map: dict[str, str], experiments_ids_map: dict[str, str]):
    """Analyze emission spectrum files, extract peak wavelengths, upload results and raw measurements."""
    for file_path in glob.glob(f"{MEASUREMENT_FOLDER}/experiment_*_measurement.csv"):
        peak_x = find_emission_spectrum_peak_wavelength(file_path)

        # Match file to experiment
        name = os.path.basename(file_path).split("_")[1]  # e.g., "01" from "experiment_01_measurement.csv"
        experiment_title = f"QD_EXP_{int(name):02d}"

        # Upload the analysis result as an item value
        if peak_x is not None:
            values = [{"parameterId": exp_col_param_map["Peak Wavelength (nm)"], "value": str(peak_x)}]
            update_item(experiments_ids_map[experiment_title], values)
            parser_code = "PL-AG-E-CC"
            file = (os.path.basename(file_path), open(file_path, "rb"), "text/csv")
            measurement_title = "Emission Spectrum"
            create_measurement(experiments_ids_map[experiment_title], measurement_title, parser_code, file)

# --- Main Logic ---
def main():
    print("=" * 60)
    print("🚀  Upload Quantum Dots Data Example")
    print("=" * 60)

    print("\n=== Step 1: Fetching Materials and Experiments data from Excel ===")
    df_materials = pd.read_excel(EXCEL_PATH, sheet_name="Materials")
    df_experiments = pd.read_excel(EXCEL_PATH, sheet_name="Experiments")

    print("\n=== Step 2: Fetching folder_id of the parent folder of the Materials and Experiments tables ===\n")
    folder_id = get_folder_id_by_name(FOLDER_TITLE)

    print("\n=== Step 3: Deleting existing tables in the folder ===\n")
    materials_table_title = "Materials"
    experiments_table_title = "Experiments"
    delete_existing_tables(folder_id, materials_table_title, experiments_table_title)

    print("\n=== Step 4: Creating the Materials table ===\n")
    materials_table_id, mat_col_param_map = create_materials_table(folder_id, materials_table_title)

    print("\n=== Step 5: Creating the Experiments table ===\n")
    experiments_table_id, exp_col_param_map, formulation_protocol_id = (
        create_experiments_table(folder_id, experiments_table_title,materials_table_id))

    print("\n=== Step 6: Uploading the Material items ===\n")
    materials_ids_map = upload_materials(materials_table_id, mat_col_param_map, df_materials)

    print("\n=== Step 7: Uploading the Experiment items ===\n")
    experiments_ids_map = upload_experiments(experiments_table_id, exp_col_param_map, materials_ids_map,
                                             formulation_protocol_id, df_experiments)

    print("\n=== Step 8: Analyzing the measurements, extracting the peak wavelength, and uploading files and results ===\n")
    upload_emission_spectrum_measurements(exp_col_param_map, experiments_ids_map)


if __name__ == "__main__":
    main()
