# MaterialsZone API Examples

This repository contains a collection of self-contained examples demonstrating how to use the [MaterialsZone REST API](https://developer.materials.zone) to interact with various elements of the platform, such as tables, protocols, parameters, items, and measurements.

Each example resides in its own subfolder under the `examples/` directory and includes its own README, code, sample input files, and dependencies. These examples are intended to help developers get started quickly and adapt the code to their own needs.

## 📚 Examples

### 1. `quantum_dot_example`

**Description:**  
This example walks through a complete flow for uploading materials and experiments related to quantum dots. It includes defining protocols, uploading composition data, processing parameters, and measurement files (emission spectra). It also performs a simple analysis on measurement files and writes the results back to the experiment table.

**Key Concepts Covered:**
- API usage
- Table, protocol and parameter creation
- Item creation and updates
- Measurement parsing and upload
- Emission spectrum analysis

---

### 2. `create_db_from_backup`

**Description:**  
This example demonstrates how to reconstruct a PostgreSQL database from a MaterialsZone backup, which consists of CSV files and measurement files. It creates the necessary table schemas, populates the tables with data, and provides methods to interact with the database.

Once the database is populated, it shows how to:
- Execute SQL queries directly on the database.
- Load data into Pandas DataFrames for further analysis and processing.

This is particularly useful for users working with exported or archived data.

**Key Concepts Covered:**
- PostgreSQL database setup from CSV backups
- Schema creation and data ingestion
- SQL querying of a table
- Pandas-based querying of a table

---

### 3. `parser_manager_cli`

**Description:**  
This example demonstrates how to use the parser APIs to manage parsers. In this example, we build a CLI (Command-Line Interface) tool that can be used by a user to list all parsers, show details of a parser, and create, update and delete parsers.

Once a parser is created, it may be used to parse files output by scientific instruments into a MaterialsZone common format, which can then be viewed in various graphs.

**Key Concepts Covered:**
- Getting all parsers that are accessible to my organization (both system parser and parsers created by members of the organization)
- Getting a specific parser
- Creating a parser
- Updating a parser
- Deleting a parser

---

More examples will be added over time to cover different use cases and data types.

---

For more information, please visit our [Developer Portal](https://developer.materials.zone).
