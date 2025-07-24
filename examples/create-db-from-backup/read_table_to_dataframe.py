import os
import psycopg2
import pandas as pd

# Define the table_id to filter on
table_id = '<your table id>'  # Replace with your actual UUID

# Connect to PostgreSQL using environment variables
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_DATABASE"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

# Updated SQL query including ranks
query = """
SELECT 
    ti.title AS title, 
    tpr.title AS protocol,
    tpr.rank AS protocol_rank, 
    COALESCE(tp.title, ti3.title) AS parameter, 
    tp.rank AS parameter_rank,
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
WHERE t.id = %s
ORDER BY ti.title, tpr.rank, tp.rank;
"""

# Load query results into DataFrame
df_long = pd.read_sql_query(query, conn, params=[table_id])

# Consolidate the value into one column
def coalesce_value(row):
    return (
        row["quantity"] if pd.notnull(row["quantity"]) else
        row["text"] if pd.notnull(row["text"]) else
        row["boolean"] if pd.notnull(row["boolean"]) else
        row["enum"] if pd.notnull(row["enum"]) else
        row["link"]
    )

df_long["value"] = df_long.apply(coalesce_value, axis=1)

# Construct a multi-index header using rank to sort later
df_long["column_key"] = list(zip(
    df_long["protocol_rank"], 
    df_long["parameter_rank"], 
    df_long["protocol"], 
    df_long["parameter"]
))

# Sort the unique headers by rank
column_order = sorted(df_long["column_key"].unique())

# Create a mapping from (protocol, parameter) to ordered column name
col_name_map = {
    key: f"{key[2]} | {key[3]}"  # use protocol | parameter for display
    for key in column_order
}

# Map the column_key to final column names
df_long["protocol_parameter"] = df_long["column_key"].map(col_name_map)

# Pivot to wide format
df_wide = df_long.pivot_table(
    index="title",
    columns="protocol_parameter",
    values="value",
    aggfunc="first"
).reset_index()

# Enforce column order: "title" first, then ranked protocol-parameter columns
ordered_columns = ["title"] + [col_name_map[key] for key in column_order]
df_wide = df_wide[[col for col in ordered_columns if col in df_wide.columns]]

# Preview the result
print(df_wide.head())