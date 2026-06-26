# XRD Folder Watcher

X-ray diffraction (XRD) is a characterization technique used to identify the crystalline phases present in a material sample and quantify their weight percentages — a result known as a phase-composition profile. XRD instruments and analysis software (such as Jade or HighScore) export these results as files to the local computer.

This example demonstrates how to build an automation that watches a local folder where XRD result files are exported and automatically uploads the phase composition data to MaterialsZone. Once in the platform, the data is available for searching, visualization, and machine learning modeling across experiments.

## 🧰 Prerequisites

- Python 3.10+
- A valid API key for the MaterialsZone REST API
- An existing folder in MaterialsZone where the tables will be created

## 🚀 What the Scripts Do

This example is split into two scripts:

| Script | Purpose | When to run |
|---|---|---|
| `setup.py` | Creates the XRD Phases and Materials tables with their protocols and parameters | Once, for initial setup |
| `watcher.py` | Scans a local folder every 10 seconds and uploads any new or changed CSV files | Kept running in the background |

The data model uses two tables. **XRD Phases** stores the set of known crystalline phases, with each phase as a separate item. **Materials** stores the material samples. The phase composition of each material — which phases are present and at what weight percentage — is stored in the material item as a formulation protocol that references the corresponding phase items in the XRD Phases table.

## 📦 Setup Instructions

1. **Clone this repository (skip if you already cloned it for another example; run `git pull` to get the latest)**:
   ```bash
   git clone https://github.com/materialscloud/materials-zone-api-examples.git
   cd materials-zone-api-examples
   ```

2. **Switch to the example's directory**:
   ```bash
   cd examples/xrd_folder_watcher/
   ```

3. **Ensure Python 3.10 or higher is installed**:
   ```bash
   python --version
   ```

4. **(Recommended) Create and activate a virtual environment**:
   - **macOS / Linux**
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   - **Windows**
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Set your API key** — copy the example env file and fill in your key:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and replace `your_api_key_here` with your actual MaterialsZone API key.

7. **Create a folder in MaterialsZone** and name it `XRD Folder Watcher` (or update `FOLDER_TITLE` in `setup.py` to match your folder name).

8. **Run the setup script** (this runs once):
   ```bash
   python setup.py
   ```
   At the end, it will print two table IDs:
   ```
   Setup complete! Paste these IDs into .env:
     MATERIALS_TABLE_ID  = "abc123..."
     XRD_PHASES_TABLE_ID = "def456..."
   ```

9. **Paste the printed IDs into `.env`**:
   Open `.env` and fill in `MATERIALS_TABLE_ID` and `XRD_PHASES_TABLE_ID`.

10. **Start the watcher**:
    ```bash
    python watcher.py
    ```
    The watcher will print a confirmation that it is connected and running, then begin polling the folder.

11. **Test with the sample files** — copy them into the `incoming/` folder:
    ```bash
    cp sample_files/MAT-001.csv incoming/
    cp sample_files/MAT-002.csv incoming/
    ```
    Within one scan interval the watcher will detect and process them, printing progress to the terminal. Open the Materials table in MaterialsZone to verify the uploaded compositions.

12. **Press Ctrl+C** to stop the watcher when you are done.

## 📁 File Structure

```
xrd_folder_watcher/
├── setup.py              # Run once: creates table structure, prints IDs to paste into .env
├── watcher.py            # Run continuously: scans folder and uploads new files
├── parser.py             # Reads a phase,wt_pct CSV and returns structured data
├── mz_operations.py      # MZ-specific operations (find/create items, upload composition, etc.)
├── mz_api_helpers.py     # Low-level HTTP helpers for the MaterialsZone REST API
├── tracker.py            # Detects new and changed files using MD5 hashing
├── config.py             # Configuration: folder path, scan interval
├── sample_files/         # Synthetic example input files
│   ├── MAT-001.csv
│   └── MAT-002.csv
├── incoming/             # Drop XRD result files here (created automatically on first run)
├── requirements.txt
└── README.md
```

`processed.json` is created automatically in the working directory the first time a file is processed. It stores the upload status and MD5 hash for each file seen so far.

## 📂 Input File Format

Each CSV file has two sections introduced by a header row:

```csv
param,value
crystallinity_pct,94.9

phase,formula,wt_pct,pdf_num
Quartz,SiO2,45.2,04-012-0490
Calcite,Ca(CO3),32.1,00-066-0867
Feldspar,KAlSi3O8,22.7,01-084-1302
```

- **Filename without extension = sample ID** — the watcher looks up an item with that title in the Materials table (`MAT-001.csv` → item `MAT-001`).
- **param section** — one row per sample-level parameter. The key must match what `watcher.py` expects.
- **phase section** — one row per crystalline phase. `formula` and `pdf_num` are optional but recommended: `pdf_num` is the ICDD Powder Diffraction File card number; `formula` is the chemical formula. Both are stored on the phase item in the XRD Phases table the first time that phase is seen.

If a phase or material item is not yet in MaterialsZone it will be created automatically by the watcher the first time it is encountered.

To adapt this example to your own instrument's export format, replace the body of `parse_xrd_file()` in `parser.py`.

## 🔁 Re-uploading Updated Files

If you save a new version of a file with the same name, the watcher detects the change via MD5 hash and re-processes it: existing composition values are cleared first, then the new data is uploaded. Files that have not changed since the last run are silently skipped.

## 🔧 Extending This Example

### Adapting to your instrument's file format

The example uses a CSV with `phase,formula,wt_pct,pdf_num` columns as the input format. XRD analysis software typically exports results in its own text or XML format (for example, Jade produces a structured `.wpf.txt` report). To use this watcher with your instrument:

1. Replace the body of `parse_xrd_file()` in `parser.py`. The function must return a dict with `params` and `phases` keys, where each phase has at least `phase` and `wt_pct` fields; `formula` and `pdf_num` are optional.
2. Update the glob pattern in `watcher.py` (`watch_folder.glob("*.csv")`) to match your instrument's file extension — for example `"*.txt"` or `"*.wpf.txt"`.

### Extracting the sample ID from a filename convention

This example uses the full filename stem as the sample ID (`MAT-001.csv` → `MAT-001`). If your instrument uses a longer naming convention where the sample ID is a prefix or sub-string of the filename, change the one line in `watcher.py` that reads:

```python
sample_id = file_path.stem
```

Replace it with the extraction logic your convention requires — for example, a `re.match` on `file_path.name` to capture the ID portion.

### Storing additional parameters from the report

The Materials table already has an **Analysis** protocol with one parameter: **Crystallinity (%)**. The full upload flow for this parameter is implemented end-to-end as a working example — from the CSV file through `parser.py`, `setup.py`, and `watcher.py`.

To add more parameters, follow the same pattern:
1. Add a row to the `param` section of your CSV files.
2. Add the parameter to the `Analysis` protocol in `setup.py` using `ops.create_quantity_parameter`.
3. Look up its ID at startup in `watcher.py` using `ops.get_parameter_id`, and add an upload line following the existing `crystallinity_pct` example.

### Watching multiple folders

To watch more than one folder — for example one per instrument — run a separate instance of `watcher.py` for each, each with its own `config.py` pointing to a different `WATCH_FOLDER` and `PROCESSED_LOG` path. The Materials and XRD Phases tables can be shared across instances.

## 📌 Next Steps

- **Run as a background service** — on macOS use `launchd`, on Linux `systemd`, on Windows the Task Scheduler to start `watcher.py` automatically at login.
