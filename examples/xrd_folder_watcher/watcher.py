"""
watcher.py

Watches a local folder for new XRD result files and uploads them to MaterialsZone.

Run this script in the background after completing setup.py and filling in .env.
Every SCAN_INTERVAL_SEC seconds it scans WATCH_FOLDER for new or changed CSV files.
For each one, it parses the phase composition and sample-level parameters, then
uploads them to the matching material item in MaterialsZone.
"""

import time
from pathlib import Path
from datetime import datetime

import config
import tracker
import parser as xrd_parser
import mz_operations as ops


def process_file(file_path: Path, formulation_protocol_id: str,
                 crystallinity_parameter_id: str, pdf_parameter_id: str,
                 formula_parameter_id: str) -> None:
    """Parse a result file and upload its data to MaterialsZone."""
    sample_id = file_path.stem  # filename without extension is the sample ID

    print(f"\n[{_now()}] Processing {file_path.name}")

    item = ops.get_item_by_title(config.MATERIALS_TABLE_ID, sample_id)
    if item is None:
        item = ops.create_item(config.MATERIALS_TABLE_ID, sample_id)
        print(f"  ✓ Created new material item '{sample_id}'")

    result = xrd_parser.parse_xrd_file(file_path)
    phases = result["phases"]
    params = result["params"]
    print(f"  ✓ Parsed {len(phases)} phases from {file_path.name}")

    # Clear any existing composition before uploading fresh values.
    # This prevents duplicate entries when an updated file is re-processed.
    ops.clear_composition(item["id"], formulation_protocol_id)

    # Resolve each phase name to an item ID in the XRD Phases table.
    # ensure_phase_item creates the phase automatically if it doesn't exist yet,
    # and fills in formula/PDF-# on existing items if those fields are still empty.
    phase_entries = []
    for row in phases:
        phase_item_id = ops.ensure_phase_item(
            config.XRD_PHASES_TABLE_ID, row["phase"],
            pdf_parameter_id, row["pdf_num"],
            formula_parameter_id, row["formula"],
        )
        phase_entries.append({"phase_item_id": phase_item_id, "wt_pct": row["wt_pct"]})

    ops.upload_composition(item["id"], formulation_protocol_id, phase_entries)
    print(f"  ✓ Uploaded XRD composition for '{sample_id}'")

    # Upload sample-level parameters from the param section of the CSV
    if "crystallinity_pct" in params:
        ops.update_item(item["id"], [
            {"parameterId": crystallinity_parameter_id, "value": params["crystallinity_pct"]}
        ])
        print(f"  ✓ Uploaded analysis parameters for '{sample_id}'")

    ops.upload_file(item["id"], file_path)

    tracker.record(file_path.name, file_path, "uploaded", config.PROCESSED_LOG)
    print(f"  ✓ Done")


def _now() -> str:
    """Return a short HH:MM:SS timestamp for log lines."""
    return datetime.now().strftime("%H:%M:%S")


def _validate_config() -> None:
    """Raise a clear error if table IDs are missing from .env."""
    if not config.MATERIALS_TABLE_ID or not config.XRD_PHASES_TABLE_ID:
        raise RuntimeError(
            "MATERIALS_TABLE_ID and XRD_PHASES_TABLE_ID are not set in .env.\n"
            "Run setup.py first and paste the printed IDs into .env."
        )


def main():
    _validate_config()

    watch_folder = Path(config.WATCH_FOLDER)
    watch_folder.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("XRD Folder Watcher — Running")
    print("=" * 60)
    print(f"  Watching : {watch_folder.resolve()}")
    print(f"  Interval : every {config.SCAN_INTERVAL_SEC} seconds")
    print(f"  Press Ctrl+C to stop.\n")

    # Look up protocol and parameter IDs once at startup rather than on every scan
    formulation_protocol_id = ops.get_formulation_protocol_id(
        config.MATERIALS_TABLE_ID, "XRD Composition"
    )
    crystallinity_parameter_id = ops.get_parameter_id(
        config.MATERIALS_TABLE_ID, "Analysis", "Crystallinity (%)"
    )
    pdf_parameter_id = ops.get_parameter_id(
        config.XRD_PHASES_TABLE_ID, "Properties", "PDF-#"
    )
    formula_parameter_id = ops.get_parameter_id(
        config.XRD_PHASES_TABLE_ID, "Properties", "Formula"
    )
    print(f"  ✓ Connected to MaterialsZone\n")

    while True:
        pending = [
            f for f in watch_folder.glob("*.csv")
            if tracker.needs_processing(f.name, f, config.PROCESSED_LOG)
        ]

        for file_path in pending:
            try:
                process_file(file_path, formulation_protocol_id,
                             crystallinity_parameter_id, pdf_parameter_id,
                             formula_parameter_id)
            except Exception as e:
                print(f"  ✗ [{_now()}] Failed to process {file_path.name}: {e}")
                tracker.record(file_path.name, file_path, "failed", config.PROCESSED_LOG)

        time.sleep(config.SCAN_INTERVAL_SEC)


if __name__ == "__main__":
    main()
