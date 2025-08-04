import os
import csv
import json
from typing import Union, List, Dict, Any
from .db_manager import DBManager


def load_table(
    table_name: str,
    data_source: Union[str, List[Dict[str, Any]]],
    db_path: str,
):
    """
    Loads structured data into an SQLite table.
    Supports CSV file, JSON file, or list of dicts as data_source.
    Dynamically creates table and columns as needed.
    Prevents duplicate insertions if 'id' field is present.
    All columns are stored as TEXT.
    """
    # Step 1: Parse the data_source into a list of dicts
    data_rows = []

    if isinstance(data_source, str):
        # It's a file path
        if not os.path.exists(data_source):
            raise FileNotFoundError(f"File not found: {data_source}")

        ext = os.path.splitext(data_source)[1].lower()
        if ext == ".csv":
            with open(data_source, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                data_rows = [dict(row) for row in reader]
        elif ext == ".json":
            with open(data_source, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("JSON file must contain a list of objects")
                data_rows = [dict(row) for row in data]
        else:
            raise ValueError("Unsupported file type. Only CSV and JSON are supported.")
    elif isinstance(data_source, list):
        # Assume it's a list of dicts
        if not all(isinstance(row, dict) for row in data_source):
            raise ValueError("All items in data_source list must be dictionaries")
        data_rows = [dict(row) for row in data_source]
    else:
        raise ValueError("data_source must be a file path or a list of dictionaries")

    if not data_rows:
        raise ValueError("No data to load.")

    # Step 2: Connect to the database
    db = DBManager(db_path)

    try:
        # Step 3: Ensure table exists and has all columns
        data_columns = set()
        for row in data_rows:
            data_columns.update(row.keys())
        data_columns = list(data_columns)

        if not db.table_exists(table_name):
            db.create_table(table_name, data_columns)
        else:
            # Add any missing columns
            existing_columns = db.get_table_columns(table_name)
            missing_columns = [col for col in data_columns if col not in existing_columns]
            if missing_columns:
                db.add_columns(table_name, missing_columns)

        # Step 4: Insert rows, preventing duplicates if 'id' is present
        db.insert_rows(table_name, data_rows, prevent_duplicates=True)
    finally:
        db.close()
