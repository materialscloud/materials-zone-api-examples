# Create PostgreSQL Tables from MaterialsZone Backup

The script (`create_db_from_backup.py`) creates tables in a PostgreSQL database from the CSV files of a MaterialsZone backup. It connects to the database, creates tables based on CSV metadata, enforces primary and foreign key constraints, and imports the data from the CSV files.

## 🧰 Prerequisites

- Python 3.8+
- A running PostgreSQL database
- A MaterialsZone backup (the `database` and `files` folders)

## 🚀 What the Script Does

1. **Connects to your PostgreSQL database** using the connection environment variables.
2. **Creates the tables** based on the backup's CSV metadata (without dropping existing ones).
3. **Enforces primary and foreign key constraints** between the tables.
4. **Imports the CSV data** into the corresponding tables.

## 📦 Setup Instructions

1. **Clone this repository** (skip if you already cloned it for another example; run `git pull` to get the latest):
   ```bash
   git clone https://github.com/materialscloud/materials-zone-api-examples.git
   cd materials-zone-api-examples
   ```

2. **Switch to the example's directory**:
   ```bash
   cd examples/create_db_from_backup/
   ```

3. **Ensure Python 3.8 or higher is installed**:
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

6. **Add your MaterialsZone backup**:
   Create a directory called `backup` inside this example's folder. Unzip your MaterialsZone backup and copy the `database` and `files` folders into it, so the layout looks like:
   ```
   create_db_from_backup/
   └── backup/
       ├── database/
       │   ├── folders.csv
       │   ├── table_files.csv
       │   ├── table_items.csv
       │   ├── table_parameter_enum_values.csv
       │   ├── table_parameters.csv
       │   ├── table_protocols.csv
       │   ├── table_values.csv
       │   └── tables.csv
       └── files/
           └── ...
   ```

7. **Set your PostgreSQL connection details** (via environment variables):
   - **macOS / Linux**
     ```bash
     export DB_HOST=localhost
     export DB_PORT=5432
     export DB_DATABASE=your_database
     export DB_USER=your_username
     export DB_PASSWORD=your_password
     ```
   - **Windows (Command Prompt)**
     ```cmd
     set DB_HOST=localhost
     set DB_PORT=5432
     set DB_DATABASE=your_database
     set DB_USER=your_username
     set DB_PASSWORD=your_password
     ```

8. **Run the script**:
   ```bash
   python create_db_from_backup.py
   ```
   This connects to your database, creates the tables, enforces the constraints, and inserts the CSV data.

## 📁 File Structure

```
create_db_from_backup/
├── create_db_from_backup.py    # The main script: creates tables and imports the backup
├── read_table_to_dataframe.py  # Loads a table into a pandas DataFrame (see below)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── backup/                     # Your MaterialsZone backup (you provide this — see setup)
    ├── database/               # CSV files exported from MaterialsZone
    └── files/                  # Attached files from the backup
```

## 📊 Querying a Table Using SQL or Pandas

To retrieve all values stored in a specific table with their associated metadata, use the following SQL query:

```sql
SELECT ti.title item, 
       tpr.title protocol, 
       CASE 
           WHEN tp.title IS NOT NULL THEN tp.title 
           ELSE ti3.title 
       END AS parameter, 
       tv.quantity, 
       tp.unit, 
       tv."text", 
       tv."boolean", 
       tpe.value AS enum, 
       ti2.title AS link
FROM tables t
JOIN table_items ti ON ti.table_id = t.id
JOIN table_protocols tpr ON tpr.table_id = t.id
JOIN table_parameters tp ON tp.table_protocol_id = tpr.id
JOIN table_values tv ON tv.table_item_id = ti.id AND tv.table_parameter_id = tp.id
LEFT JOIN table_parameter_enum_values tpe ON tpe.id = tv.enum_value
LEFT JOIN table_items ti2 ON ti2.id = tv.link
LEFT JOIN table_items ti3 ON ti3.id = tp.title_table_item_id
WHERE t.id = '<table id>'
ORDER BY ti.title, tpr.title, tp.title;
```

This query produces a **"long" presentation** of the data, meaning each row represents a single value recorded in the table. Each row includes the item, protocol, parameter, and the actual value (whether numeric, text, boolean, enum, or link to another item).

The script `read_table_to_dataframe.py` loads the result of this query into a pandas DataFrame and converts it to a standard table as displayed in the MaterialsZone platform — the columns are the table's parameters, the rows are the items, and the cells are the values. Use it by setting the `table_id` variable to the UUID of your table and running:

```bash
python read_table_to_dataframe.py
```

## 📌 Next Step

You can now adjust the scripts to suit your own database and tables! Explore `create_db_from_backup.py` to understand the import workflow and `read_table_to_dataframe.py` to query your data.

---

Happy experimenting! ✨
