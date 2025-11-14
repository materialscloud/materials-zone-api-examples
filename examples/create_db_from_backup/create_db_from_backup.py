import os
import pandas as pd
import psycopg2
from psycopg2 import sql
from pathlib import Path

# Load environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# CSV file paths
database_path = Path(__file__).parent / "backup" / "database"
file_paths = {
    "folders": database_path / "folders.csv",
    "tables": database_path / "tables.csv",
    "table_items": database_path / "table_items.csv",
    "table_protocols": database_path / "table_protocols.csv",
    "table_parameters": database_path / "table_parameters.csv",
    "table_parameter_enum_values": database_path / "table_parameter_enum_values.csv",
    "table_values": database_path / "table_values.csv",
    "table_files": database_path / "table_files.csv",
}

# FIXME: clean value and parameters that refer to trashed table items
df_table_items = pd.read_csv(file_paths["table_items"])
df_table_parameters = pd.read_csv(file_paths["table_parameters"])
df_table_values = pd.read_csv(file_paths["table_values"])
valid_table_item_ids = set(df_table_items['id'].dropna())
df_table_parameters = df_table_parameters[
    df_table_parameters['title_table_item_id'].isna() |
    df_table_parameters['title_table_item_id'].isin(valid_table_item_ids)
]
df_table_values = df_table_values[
    df_table_values['table_item_id'].isin(valid_table_item_ids)
]
valid_table_parameter_ids = set(df_table_parameters['id'].dropna())
df_table_values = df_table_values[
    df_table_values['table_parameter_id'].isin(valid_table_parameter_ids)
]
df_table_parameters.to_csv(file_paths["table_parameters"], index=False)
df_table_values.to_csv(file_paths["table_values"], index=False)

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# SQL statements to create tables
create_statements = {
    "folders": """
        CREATE TABLE IF NOT EXISTS folders (
            id UUID PRIMARY KEY,
            title TEXT,
            parent_folder_id UUID,
            created_timestamp TIMESTAMP,
            updated_timestamp TIMESTAMP,
            FOREIGN KEY (parent_folder_id) REFERENCES folders(id) DEFERRABLE INITIALLY DEFERRED
        );
    """,
    "tables": """
        CREATE TABLE IF NOT EXISTS tables (
            id UUID PRIMARY KEY,
            title TEXT,
            folder_id UUID,
            created_timestamp TIMESTAMP,
            updated_timestamp TIMESTAMP,
            FOREIGN KEY (folder_id) REFERENCES folders(id)
        );
    """,
    "table_items": """
        CREATE TABLE IF NOT EXISTS table_items (
            id UUID PRIMARY KEY,
            code TEXT,
            title TEXT,
            description TEXT,
            table_id UUID,
            created_timestamp TIMESTAMP,
            timestamp TIMESTAMP,
            updated_timestamp TIMESTAMP,
            FOREIGN KEY (table_id) REFERENCES tables(id)
        );
    """,
    "table_protocols": """
        CREATE TABLE IF NOT EXISTS table_protocols (
            id UUID PRIMARY KEY,
            title TEXT,
            description TEXT,
            table_id UUID,
            rank INTEGER,
            type TEXT,
            unit TEXT,
            created_timestamp TIMESTAMP,
            updated_timestamp TIMESTAMP,
            FOREIGN KEY (table_id) REFERENCES tables(id)

        );
    """,
    "table_parameters": """
        CREATE TABLE IF NOT EXISTS table_parameters (
            id UUID PRIMARY KEY,
            title TEXT,
            title_table_item_id UUID,
            table_protocol_id UUID,
            rank INTEGER,
            value_type TEXT,
            unit TEXT,
            created_timestamp TIMESTAMP,
            updated_timestamp TIMESTAMP,
            FOREIGN KEY (title_table_item_id) REFERENCES table_items(id),
            FOREIGN KEY (table_protocol_id) REFERENCES table_protocols(id)
        );
    """,
    "table_parameter_enum_values": """
        CREATE TABLE IF NOT EXISTS table_parameter_enum_values (
            id UUID PRIMARY KEY,
            table_parameter_id UUID,
            value TEXT,
            rank INTEGER,
            FOREIGN KEY (table_parameter_id) REFERENCES table_parameters(id)
        );
    """,
    "table_values": """
        CREATE TABLE IF NOT EXISTS table_values (
            table_item_id UUID,
            table_parameter_id UUID,
            quantity FLOAT,
            text TEXT,
            boolean BOOLEAN,
            link UUID,
            enum_value UUID,
            FOREIGN KEY (table_item_id) REFERENCES table_items(id),
            FOREIGN KEY (table_parameter_id) REFERENCES table_parameters(id),
            FOREIGN KEY (enum_value) REFERENCES table_parameter_enum_values(id),
            FOREIGN KEY (link) REFERENCES table_items(id)
        );
    """,
    "table_files": """
        CREATE TABLE IF NOT EXISTS table_files (
            id UUID PRIMARY KEY,
            title TEXT,
            table_item_id UUID,
            raw_filename TEXT,
            created_timestamp TIMESTAMP,
            updated_timestamp TIMESTAMP,
            FOREIGN KEY (table_item_id) REFERENCES table_items(id)
        );
    """
}

# Create all tables
for name, statement in create_statements.items():
    cur.execute(statement)

conn.commit()

# Load data into tables
conn.autocommit = False  # Start a transaction
cur.execute("BEGIN")

try: 
    for name, path in file_paths.items():
        df = pd.read_csv(path)

        # Clean and parse custom timestamp strings
        for col in df.columns:
            if 'timestamp' in col and df[col].notna().any():
                df[col] = pd.to_datetime(df[col].str.extract(r'^(.*GMT[+-]\d{4})')[0], utc=True)

        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) ON CONFLICT DO NOTHING").format(
            sql.Identifier(name),
            sql.SQL(columns),
            sql.SQL(placeholders)
        )
        for row in df.itertuples(index=False, name=None):
            row = tuple(None if pd.isna(x) else x for x in row)
            cur.execute(insert_query, row)

    conn.commit()

except Exception as e:
    conn.rollback()
    raise

cur.close()
conn.close()
