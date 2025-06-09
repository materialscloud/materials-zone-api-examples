"""
main.py

This is the main script that runs the full example workflow.

It reads your data from an Excel file, sets up the necessary tables and protocols
in your MaterialsZone folder, uploads materials and experiments, and processes
emission spectrum files.

To run the full example, just execute this file. Make sure you've set your API key
in the environment and placed your Excel and CSV files in the correct locations.
"""

import pandas as pd
from mz_operations import (
    get_folder_id_by_name,
    get_tables_in_folder,
    create_table,
    delete_table,
    create_item,
    create_protocols_and_parameters
)
from analysis import upload_emission_spectrum_measurements

EXCEL_PATH = "quantum_dot_example.xlsx"
FOLDER_TITLE = "Quantum Dot Example" # Replace with the title of the folder you created

def delete_existing_tables(folder_id: str, materials_table_title, experiments_table_title):
    """Delete tables with given titles from the specified folder if they exist. Note that the Formulations table
    must be deleted before the Materials table since it refers to it."""
    tables = get_tables_in_folder(folder_id)

    materials_table_id = next((table["id"] for table in tables if table["title"] == materials_table_title), None)
    experiments_table_id = next((table["id"] for table in tables if table["title"] == experiments_table_title), None)

    if experiments_table_id:
        delete_table(experiments_table_id)
    if materials_table_id:
        delete_table(materials_table_id)

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
    mat_col_param_map = create_protocols_and_parameters(materials_table_id, materials_table_protocols)

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
    exp_col_param_map = create_protocols_and_parameters(table_id, protocols)
    formulation_protocol_id = [protocol["id"] for protocol in protocols if protocol["title"] == "Formulation"][0]

    return table_id, exp_col_param_map, formulation_protocol_id

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

    print("\n=== Step 8: Analyzing the measurements, extracting the peak wavelength, and uploading files"
          " and results ===\n")
    upload_emission_spectrum_measurements(exp_col_param_map, experiments_ids_map)

if __name__ == "__main__":
    main()
