
# Create PostgreSQL Tables from MaterialsZone Backup

The script (`create_db_from_backup.py`) creates tables in a PostgreSQL database from the CSV files of a MaterialsZone backup.
The script connects to a PostgreSQL database, creates tables based on CSV metadata, enforces primary and foreign key constraints, and imports data from CSV files into the database.

---

## 📁 Required CSV Files

Create a directory called **backup** in the **same directory** as this script. Unzip the backup and copy the folders **database** and **files** into the **backup** directory. Your project should look like this:

```
project-root/
├── create_db_from_backup.py
├── README.md
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

---

## 🔐 Environment Variables

Before running the script, set the following environment variables for your PostgreSQL connection:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_DATABASE=your_database
export DB_USER=your_username
export DB_PASSWORD=your_password
```

These variables are used to securely connect to your PostgreSQL instance.

---

## 📦 Dependencies

Install the required Python packages either poetry by running

```bash
poetry install
```

or by installing directly with `pip`:

```bash
pip install pandas psycopg2-binary
```

---

## ▶️ Running the Script

Once the environment variables are set and CSV files are in place, run the following command in your terminal:

```bash
python create_db_from_backup.py
```

This will:
- Connect to your PostgreSQL database
- Create the necessary tables (without dropping existing ones)
- Enforce primary and foreign key constraints
- Insert CSV data into the corresponding tables

---

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

This query produces a **"long" presentation** of the data, meaning each row represents a single value recorded in the table. Each row includes the item, protocol, parameter, actual value (whether numeric, text, boolean, enum or link to another item).

The script `read_table_to_dataframe.py` loads the result of this query into a Pandas DataFrame and converts it to a standard table as it is displayed in the MaterialsZone platform, such that the columns are the parameters of the table, the rows are the items, and the cells are the values. Use the script by setting the `table_id` variable to the UUID of your table and then run the following command in your terminal:

```bash
python read_table_to_dataframe.py
```
