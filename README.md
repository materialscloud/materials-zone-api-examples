# MaterialsZone API Examples

This repository contains a collection of self-contained examples demonstrating how to use the [MaterialsZone REST API](https://developer.materials.zone) to interact with various elements of the platform, such as tables, protocols, parameters, items, and measurements.

Each example resides in its own subfolder under the `examples/` directory and includes its own README, code, sample input files, and dependencies. These examples are intended to help developers get started quickly and adapt the code to their own needs.

## 📚 Examples

### 1. Upload lab data and measurements end to end

**Folder:** [`examples/quantum_dot_api_example`](examples/quantum_dot_api_example)

**Description:**  
An end-to-end example from the quantum dots domain that walks through a complete data upload flow. It defines the tables, protocols and parameters, uploads materials and experiments with their composition and processing data, and uploads the measurement files produced by the instrument. It then runs a simple analysis on the measurements and writes the results back to the experiments table.

This is a good starting point if you want to bring your own lab data into MaterialsZone programmatically, from setting up the data structure to analyzing the uploaded measurements.

**Key Concepts Covered:**
- Table, protocol and parameter creation
- Item creation and updates
- Measurement parsing and upload
- Analyzing measurement data and writing results back to items

---

### 2. Automate uploads from an instrument's export folder

**Folder:** [`examples/xrd_folder_watcher`](examples/xrd_folder_watcher)

**Description:**  
An automation example from the X-ray diffraction (XRD) domain. It watches a local folder where an instrument's analysis software exports its result files, and automatically uploads new and changed files to MaterialsZone, so the data is available for search, visualization and modeling without manual uploads.

The example is split into a setup script that runs once to create the table structure, and a watcher script that keeps running in the background and scans the folder at a configurable interval. It is a useful template for connecting any instrument that exports files to a local folder, since the file parser can be replaced to support other formats.

**Key Concepts Covered:**
- Table, protocol and parameter creation
- Formulation protocols that reference items in another table
- Finding or creating items by title
- Detecting new and changed files and re-uploading updated data
- Running a periodic folder-watching automation

---

### 3. Manage parsers

**Folder:** [`examples/parser_manager_cli`](examples/parser_manager_cli)

**Description:**  
This example demonstrates how to use the MaterialsZone API to manage parsers, by building a simple command-line interface (CLI) to list, view, create, update and delete them.

Parsers convert files output by scientific instruments into the MaterialsZone common format, which can then be viewed in various graphs. This example is useful if you want to manage your organization's parsers from code or scripts. For an example of using parsers to upload measurement files, see `quantum_dot_api_example`.

**Key Concepts Covered:**
- Listing the parsers accessible to your organization
- Getting a specific parser
- Creating, updating and deleting parsers

---

### 4. Rebuild a backup as a local database and query it

**Folder:** [`examples/create_db_from_backup`](examples/create_db_from_backup)

**Description:**  
This example demonstrates how to reconstruct a PostgreSQL database from a MaterialsZone backup, which consists of CSV files and measurement files. It creates the table schemas and populates them with the backup data.

Once the database is populated, it shows how to query the data either directly with SQL or by loading it into Pandas DataFrames for further analysis. This is particularly useful if you work with exported or archived data, or want to analyze your data with your own tools outside the platform.

**Key Concepts Covered:**
- PostgreSQL database setup from CSV backups
- Schema creation and data ingestion
- SQL querying of a table
- Pandas-based querying of a table

---

More examples will be added over time to cover different use cases and data types.

---

For more information, please visit our [Developer Portal](https://developer.materials.zone).
