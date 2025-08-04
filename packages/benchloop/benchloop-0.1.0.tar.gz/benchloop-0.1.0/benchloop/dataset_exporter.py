import sqlite3
import json
from typing import List, Dict, Optional

def export_training_dataset(
    table_name: str,
    prompt_template: str,
    response_column: str,
    output_file: str,
    db_path: str,
    filters: Optional[Dict] = None,
    format: str = "messages"
):
    """
    Export rows from a SQLite table as a JSONL dataset for LLM training.

    Each line in the output file will be a JSON object, with prompt and response
    substituted from the table, in the specified format.

    Parameters:
        table_name (str): Name of the table to export from.
        prompt_template (str): Prompt template with placeholders like {variable}.
        response_column (str): Name of the column containing the LLM response.
        output_file (str): Path to the output .jsonl file.
        db_path (str): Path to the SQLite database file.
        filters (Optional[Dict]): Filtering conditions (same structure as filter_rows).
        format (str): "messages" (default) or "input/output".

    Raises:
        ValueError: If columns or variables are missing.
        IOError: If file writing fails.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get table columns
    cursor.execute(f"PRAGMA table_info({table_name});")
    table_columns = {row["name"] for row in cursor.fetchall()}
    if not table_columns:
        conn.close()
        raise ValueError(f"Table '{table_name}' does not exist or has no columns.")

    if response_column not in table_columns:
        conn.close()
        raise ValueError(f"Response column '{response_column}' does not exist in table '{table_name}'.")

    # Build WHERE clause (reuse logic from filter_rows)
    where_clauses = []
    params = []
    if filters:
        for col, cond in filters.items():
            if col not in table_columns:
                conn.close()
                raise ValueError(f"Column '{col}' does not exist in table '{table_name}'.")
            if isinstance(cond, dict):
                for op, val in cond.items():
                    op = op.upper()
                    if op == "!=":
                        where_clauses.append(f'"{col}" != ?')
                        params.append(val)
                    elif op == ">":
                        where_clauses.append(f'"{col}" > ?')
                        params.append(val)
                    elif op == "<":
                        where_clauses.append(f'"{col}" < ?')
                        params.append(val)
                    elif op == "CONTAINS":
                        where_clauses.append(f'"{col}" LIKE ?')
                        params.append(f"%{val}%")
                    elif op == "STARTSWITH":
                        where_clauses.append(f'"{col}" LIKE ?')
                        params.append(f"{val}%")
                    elif op == "IN":
                        if not isinstance(val, (list, tuple)):
                            conn.close()
                            raise ValueError(f"Value for 'IN' operator must be a list or tuple.")
                        placeholders = ", ".join(["?"] * len(val))
                        where_clauses.append(f'"{col}" IN ({placeholders})')
                        params.extend(val)
                    else:
                        conn.close()
                        raise ValueError(f"Unsupported operator: {op}")
            else:
                where_clauses.append(f'"{col}" = ?')
                params.append(cond)
    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    # Query rows
    query = f'SELECT * FROM "{table_name}" {where_sql};'
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Write to JSONL file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for row in rows:
                row_dict = dict(row)
                try:
                    prompt = prompt_template.format(**row_dict)
                except KeyError as e:
                    raise ValueError(f"Missing value for variable: {e} in row {row_dict}")
                response = row_dict.get(response_column, "")
                if response is None:
                    response = ""
                if format == "messages":
                    json_obj = {
                        "messages": [
                            {"role": "user", "content": prompt},
                            {"role": "assistant", "content": response}
                        ]
                    }
                elif format == "input/output":
                    json_obj = {
                        "input": prompt,
                        "output": response
                    }
                else:
                    raise ValueError(f"Unsupported format: {format}")
                f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")
    except Exception as e:
        raise IOError(f"Failed to write to file '{output_file}': {e}")
    finally:
        conn.close()
