import sqlite3
import os
from typing import List, Dict, Any, Optional
import openai
import json
from .db_manager import DBManager

def _build_where_clause(filters: Optional[Dict]) -> (str, list):
    """
    Build SQL WHERE clause and parameters from a filter dict.
    Supports equality and simple operators (e.g., {'col': {'!=': val}})
    """
    if not filters:
        return "", []
    clauses = []
    params = []
    for col, cond in filters.items():
        if isinstance(cond, dict):
            for op, val in cond.items():
                if op == "!=":
                    clauses.append(f'"{col}" != ?')
                    params.append(val)
                elif op == ">":
                    clauses.append(f'"{col}" > ?')
                    params.append(val)
                elif op == "<":
                    clauses.append(f'"{col}" < ?')
                    params.append(val)
                elif op == ">=":
                    clauses.append(f'"{col}" >= ?')
                    params.append(val)
                elif op == "<=":
                    clauses.append(f'"{col}" <= ?')
                    params.append(val)
                elif op.lower() == "is":
                    clauses.append(f'"{col}" IS ?')
                    params.append(val)
                else:
                    raise ValueError(f"Unsupported operator: {op}")
        else:
            if cond is None:
                clauses.append(f'"{col}" IS NULL')
            else:
                clauses.append(f'"{col}" = ?')
                params.append(cond)
    where_clause = "WHERE " + " AND ".join(clauses) if clauses else ""
    return where_clause, params

def _substitute_prompt(template: str, row: Dict[str, Any], columns_variables: List[str]) -> str:
    """
    Substitute {var} in template with values from row.
    """
    values = {col: str(row.get(col, "")) for col in columns_variables}
    try:
        return template.format(**values)
    except KeyError as e:
        raise ValueError(f"Missing value for variable: {e}")

def _ensure_columns(db: DBManager, table_name: str, columns: List[str]):
    """
    Ensure all columns exist in the table, add if missing.
    """
    existing = db.get_table_columns(table_name)
    missing = [col for col in columns if col not in existing]
    if missing:
        db.add_columns(table_name, missing)

def execute_prompt_on_table(
    table_name: str,
    prompt_template: str,
    columns_variables: List[str],
    result_mapping: Dict[str, str],
    filters: Optional[Dict] = None,
    limit: Optional[int] = None,
    model: str = "gpt-4o",
    api_key: str = "",
):
    """
    Iterate over rows, build prompt, call LLM, and write back responses.
    Supports structured (JSON) and plain text responses.
    """
    if not api_key:
        raise ValueError("API key is required for OpenAI API calls.")
    openai.api_key = api_key

    db = DBManager(db_path=os.path.abspath(db_path_from_env_or_default()))
    try:
        # Build query
        where_clause, params = _build_where_clause(filters)
        limit_clause = f"LIMIT {limit}" if limit else ""
        query = f'SELECT rowid, * FROM "{table_name}" {where_clause} {limit_clause};'
        db.cursor.execute(query, params)
        rows = db.cursor.fetchall()

        if not rows:
            print("No rows to process.")
            return

        # Determine which columns to ensure exist for results
        result_columns = list(result_mapping.values())
        _ensure_columns(db, table_name, result_columns)

        for row in rows:
            row_dict = dict(row)
            rowid = row_dict.get("id") or row_dict.get("rowid")
            prompt = _substitute_prompt(prompt_template, row_dict, columns_variables)

            # Prepare API call
            is_structured = len(result_mapping) > 1 or (len(result_mapping) == 1 and list(result_mapping.keys())[0] != "response")
            try:
                if is_structured:
                    # Use JSON mode (function calling)
                    response = openai.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant. Respond in JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"},
                    )
                    content = response.choices[0].message.content
                    try:
                        result_json = json.loads(content)
                    except Exception as e:
                        print(f"JSON parsing error for row {rowid}: {e}")
                        continue
                    update_dict = {}
                    for resp_field, db_col in result_mapping.items():
                        update_dict[db_col] = result_json.get(resp_field, "")
                else:
                    # Plain text response
                    response = openai.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt}
                        ],
                    )
                    content = response.choices[0].message.content
                    db_col = result_mapping.get("response", "response")
                    update_dict = {db_col: content}

                # Update the row in the database
                set_clause = ", ".join([f'"{col}" = ?' for col in update_dict.keys()])
                values = list(update_dict.values())
                # Prefer id if present, else rowid
                if "id" in row_dict:
                    db.cursor.execute(
                        f'UPDATE "{table_name}" SET {set_clause} WHERE id = ?;',
                        values + [row_dict["id"]],
                    )
                else:
                    db.cursor.execute(
                        f'UPDATE "{table_name}" SET {set_clause} WHERE rowid = ?;',
                        values + [rowid],
                    )
                db.conn.commit()
            except Exception as e:
                print(f"Error processing row {rowid}: {e}")
                continue
    finally:
        db.close()

def db_path_from_env_or_default():
    # Looks for BENCHLOOP_DB_PATH env var, else uses 'benchloop_test.sqlite'
    return os.environ.get("BENCHLOOP_DB_PATH", "benchloop_test.sqlite")
