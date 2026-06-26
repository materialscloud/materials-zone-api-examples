"""
parser.py

Reads an XRD result CSV file and returns sample-level parameters and phase composition.

The file has two sections, each introduced by a header row:
  - 'param,value'                   — one row per sample-level parameter (e.g. crystallinity_pct)
  - 'phase,formula,wt_pct,pdf_num'  — one row per crystalline phase; formula and pdf_num are optional

Sections are separated by an empty line. Replace or extend this file to support
your own instrument's export format.
"""

import csv


def parse_xrd_file(file_path) -> dict:
    """Parse an XRD result file and return a dict with 'params' and 'phases'.

    Returns:
      {
        "params": {key: str},
        "phases": [{"phase": str, "formula": str, "wt_pct": float, "pdf_num": str}, ...]
      }
    formula and pdf_num are empty strings when not present in the file.
    """
    params = {}
    phases = []
    mode = None
    headers = []

    with open(file_path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip():
                continue
            key = row[0].strip()
            if key == "param":
                mode = "params"
            elif key == "phase":
                mode = "phases"
                headers = [h.strip() for h in row]
            elif mode == "params":
                params[key] = row[1].strip()
            elif mode == "phases":
                row_dict = {headers[i]: row[i].strip() for i in range(min(len(headers), len(row)))}
                phases.append({
                    "phase": key,
                    "formula": row_dict.get("formula", ""),
                    "wt_pct": float(row_dict.get("wt_pct", row[1])),
                    "pdf_num": row_dict.get("pdf_num", ""),
                })

    return {"params": params, "phases": phases}
