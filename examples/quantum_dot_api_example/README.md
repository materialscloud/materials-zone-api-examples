# Quantum Dot API Example

This repository provides a simple but complete example of how to use the MaterialsZone API to create tables, protocols and parameters, upload material and experiment data from an Excel file, perform analysis on measurement data, and upload both measurement files and analysis results. The example is from the field of quantum dots, but the code can be applied to any domain.

## 🧰 Prerequisites

- Python 3.8+
- A valid API key for the MaterialsZone REST API
- Access to an existing folder in the platform (you'll provide the folder name)

## 📦 Setup Instructions

1. **Clone this repository (if you haven't already)**:
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

5. **Set your API key** (recommended via environment variable):
   
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

6. **Review the input data**:
   - `quantum_dots_example.xlsx` contains two sheets:
     - **Materials** — List of quantum dot materials with properties like band gap, size, and quantum yield.
     - **Experiments** — Fabrication experiments using the materials, with processing parameters and results.
   - A folder named `measurements/` with one CSV file per experiment (emission spectra data).
   - Note: all data is synthetic data.

7. **Create a folder in MaterialsZone**:
   - Open the MaterialsZone app.
   - Create a folder for this project.

8. **Set the `FOLDER_TITLE` variable**
   - Set the `FOLDER_TITLE` variable in the Configuration section of `upload_quantum_dots_data.py` to the folder's title.

9. **Run the script**:
   ```bash
   python upload_quantum_dots_data.py
   ```

10. **Check out the results**:

    Open the MaterialsZone app and check out the two newly created tables.

## 🚀 What the Script Does

1. **Looks up the folder ID** from the name you enter.
2. **Checks if the 'Materials' and 'Experiments' tables exist**, creates them if not.
3. **Defines the necessary parameters** in each table.
4. **Uploads one item at a time** using the REST API:
   - Each material with its properties
   - Each experiment with its setup and result
5. **Analyzes measurement data** (e.g., finds the peak wavelength in a spectrum).
6. **Uploads the analysis result** back into the experiment table as a new item.

## 📁 File Structure

```
quantum-dot-api-example/
├── quantum_dots_example.xlsx        # Excel file with materials and experiments
├── measurements/                    # Folder with measurement CSVs
│   ├── experiment_01_measurement.csv
│   ├── ...
├── upload_quantum_dot_data.py      # The main script
├── README.md                       # This file
└── requirements.txt                # Python dependencies
```

## 📌 Next Step

You can now adjust the data and script to suit your own research and use case!


---

Happy experimenting with Quantum Dots! ✨
