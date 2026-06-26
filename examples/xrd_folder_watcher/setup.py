"""
setup.py

One-time setup script for the XRD folder watcher.

Creates the 'XRD Phases' and 'Materials' tables in your MaterialsZone folder
and prints the table IDs you need to paste into .env.

All data (phase items and material items) is created automatically by watcher.py
the first time each phase name or filename is encountered.

Run this script once before starting watcher.py.
"""

import sys
import mz_operations as ops

FOLDER_TITLE = "XRD Folder Watcher"  # Name of the folder you created in MaterialsZone


def main():
    print("=" * 60)
    print("XRD Folder Watcher — One-Time Setup")
    print("=" * 60)

    print(f"\n=== Step 1: Finding folder '{FOLDER_TITLE}' ===\n")
    folder_id = ops.get_folder_id_by_name(FOLDER_TITLE)
    print(f"  ✓ Found folder (id: {folder_id})")

    existing = {t["title"]: t["id"] for t in ops.get_tables_in_folder(folder_id)}
    conflicts = [name for name in ("XRD Phases", "Materials") if name in existing]
    if conflicts:
        print("\n  ! Setup has already been run. These tables already exist in this folder:")
        for name in conflicts:
            print(f'      {name}: "{existing[name]}"')
        print("\n  Paste the existing IDs into .env, or delete the tables and re-run.")
        sys.exit(0)

    print("\n=== Step 2: Creating the XRD Phases table ===\n")
    phases_table_id = ops.create_table(folder_id, "XRD Phases")
    properties_protocol_id = ops.create_protocol(phases_table_id, "Properties")
    ops.create_text_parameter(properties_protocol_id, "Formula")
    ops.create_text_parameter(properties_protocol_id, "PDF-#")

    print("\n=== Step 3: Creating the Materials table ===\n")
    materials_table_id = ops.create_table(folder_id, "Materials")
    ops.create_formulation_protocol(materials_table_id, "XRD Composition", [phases_table_id])
    analysis_protocol_id = ops.create_protocol(materials_table_id, "Analysis")
    ops.create_quantity_parameter(analysis_protocol_id, "Crystallinity (%)", unit="%")

    print("\n" + "=" * 60)
    print("Setup complete! Paste these IDs into .env:")
    print(f'  MATERIALS_TABLE_ID={materials_table_id}')
    print(f'  XRD_PHASES_TABLE_ID={phases_table_id}')
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
