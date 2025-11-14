# Parser Manager CLI

This example shows how to use the MaterialsZone API to manage parsers through a simple command-line tool that allows you to list all organization and system parsers, view their details, and create, update, or delete them according to a definition you pass via a JSON file. For an example on how to use the parser to upload measurement files, please see the quantum_dot_api_example in this repository.

## 🧰 Prerequisites

- Python 3.11+
- A valid API key for the MaterialsZone REST API

## 📦 Setup Instructions

1. **In your terminal, navigate to the folder where you want to place this project. Then clone this repository (if you haven’t already)**:
   ```bash
   git clone https://github.com/materialscloud/materials-zone-api-examples.git
   cd materials-zone-api-examples
   ```

2. **Switch to the example's directory**:
   ```bash
   cd examples/parser_manager_cli/
   ```

3. **Ensure Python is installed on your system**:

   This project requires Python 3.13 or higher. You can check your installed version with:
   ```bash
   python --version
   
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

6. **Set your API key** (via environment variable):
   
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

7. **In your terminal, run the script to execute the full workflow**:
   ```bash
   python main.py
   ```
   The script will now create a parser using the configuration at the top of the file.

## 📁 File Structure

The `main.py` file is the starting point — it runs the full workflow and should be the only file you need to execute. The other files are helper modules:  
- `mz_operations.py` handles building requests and calling the API
- `mz_api_helpers.py` handles low-level API request functions used throughout the project

Here’s the full file structure for this project:

```
parser-manager-cli/
├── main.py                            # The main script
├── mz_operations.py                   # Helper functions for building requests and calling the apis
├── mz_api_helpers.py                  # Low-level helper functions for sending API requests
├── README.md                          # This file
└── requirements.txt                   # Python dependencies
```

## 📌 Next Step

You can now adjust the data and script to suit your own research and use case! Explore `main.py` to understand the workflow and adjust the supporting modules as needed.


---

Happy experimenting with Parsers! ✨
