# Quantum Dot API Example

This repository provides a simple but complete example of how to use the MaterialsZone API to create tables, protocols and parameters, upload material and experiment data from an Excel file, perform analysis on measurement data, and upload both measurement files and analysis results. The example is from the field of quantum dots, but the code can be applied to any domain.

## 🧰 Prerequisites

- Python 3.8+
- A valid API key for the MaterialsZone REST API
- Access to an existing folder in the platform (you'll provide the folder name)

## 🚀 What the Script Does

This example walks you through the entire workflow of uploading and analyzing quantum dot data using the MaterialsZone API.

1. **Looks up the folder ID** from the name you enter.
2. **Checks if the 'Materials' and 'Experiments' tables exist**, creates them if not.
3. **Defines the necessary protocols and parameters** in each table.
4. **Uploads one item at a time** using the REST API:
   - Each material with its properties
   - Each experiment with its setup and result
5. **Analyzes measurement data** (e.g., finds the peak wavelength in a spectrum).
6. **Uploads both the raw measurement file and the extracted analysis result** (e.g., peak wavelength) into the relevant experiment item.

## 📦 Setup Instructions

1. **In your terminal, navigate to the folder where you want to place this project. Then clone this repository (if you haven’t already)**:
   ```bash
   git clone https://github.com/materialscloud/materials-zone-api-examples.git
   cd materials-zone-api-examples
   ```

2. **Switch to the example's directory**:
   ```bash
   cd examples/quantum_dot_api_example/
   ```

3. **(Recommended) Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set your API key** (via environment variable):
   
   - **macOS / Linux**  
     ```bash
     export MZ_API_KEY="your_api_key_here"
     ```

   - **Windows (Command Prompt)**  
     ```cmd
     set MZ_API_KEY=your_api_key_here
     ```

   - **Windows (PowerShell)**  
     ```powershell
     $env:MZ_API_KEY = "your_api_key_here"
     ```

6. **Open the project directory in Windows Explorer (on Windows) or Finder (on Mac) and review the input data**:
   - `quantum_dot_example.xlsx` contains two sheets:
     - **Materials** — List of quantum dot materials with properties like band gap, size, and quantum yield.
     - **Experiments** — Fabrication experiments using the materials, with processing parameters and results.
   - A folder named `measurements/` with one CSV file per experiment (emission spectra data).
   - Note: All data is synthetic and provided solely for demonstration purposes.

7. **Log in to the MaterialsZone app and create a folder for this project**:
   - By default, the folder is assumed to be called "Quantum Dot Example", but you can choose any title you'd like and adjust the code as explained in the next step.

8. **In `main.py`, set the `FOLDER_TITLE` variable**:
   - Set the `FOLDER_TITLE` variable in the Configuration section of `main.py` to the folder's title.

9. **In your terminal, run the script to execute the full workflow**:
   ```bash
   python main.py
   ```

10. **Check out the results**:

    Log in to the MaterialsZone app and check out the two newly created tables. You should now see the Materials and Experiments tables populated with the uploaded data and measurements.

## 📁 File Structure

The `main.py` file is the starting point — it runs the full workflow and should be the only file you need to execute. The other files are helper modules:  
- `mz_operations.py` handles table and protocol creation  
- `analysis.py` handles data analysis and measurement upload  
- `mz_api_helpers.py` handles low-level API request functions used throughout the project

Here’s the full file structure for this project:

```
quantum-dot-api-example/
├── quantum_dot_example.xlsx           # Excel file with materials and experiments
├── measurements/                      # Folder with measurement CSVs
│   ├── experiment_01_measurement.csv
│   ├── ...
├── main.py                            # The main script
├── mz_operations.py                   # Helper functions for creating tables, protocols, and items
├── analysis.py                        # Functions for processing measurement data and uploading analysis results
├── mz_api_helpers.py                  # Low-level helper functions for sending API requests
├── README.md                          # This file
└── requirements.txt                   # Python dependencies
```

## 📌 Next Step

You can now adjust the data and script to suit your own research and use case! Explore `main.py` to understand the workflow and adjust the supporting modules as needed.


---

Happy experimenting with Quantum Dots! ✨
