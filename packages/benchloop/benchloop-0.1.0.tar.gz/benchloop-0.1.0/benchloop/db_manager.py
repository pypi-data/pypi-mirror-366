import sqlite3
import os
from typing import List, Dict, Any, Optional


class DBManager:
    """
    Handles direct SQLite operations for BenchLoop.
    """

    @staticmethod
    def filter_rows(
        table_name: str,
        filters: dict = None,
        mode: str = "include",
        db_path: str = ""
    ) -> list:
        """
        Filter rows from a SQLite table based on flexible filter conditions.

        Parameters:
            table_name (str): Name of the table to filter.
            filters (dict): Filtering conditions.
            mode (str): 'include' (keep matches) or 'exclude' (remove matches).
            db_path (str): Path to the SQLite database file.

        Returns:
            List[dict]: Filtered rows as list of dictionaries.

        Raises:
            ValueError: If mode is invalid or columns in filters do not exist.
        """
        import sqlite3

        if not db_path:
            raise ValueError("db_path must be provided.")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get table columns
        cursor.execute(f"PRAGMA table_info({table_name});")
        table_columns = {row["name"] for row in cursor.fetchall()}
        if not table_columns:
            conn.close()
            raise ValueError(f"Table '{table_name}' does not exist or has no columns.")

        # Build WHERE clause
        where_clauses = []
        params = []

        if filters:
            for col, cond in filters.items():
                if col not in table_columns:
                    conn.close()
                    raise ValueError(f"Column '{col}' does not exist in table '{table_name}'.")

                # Operator logic
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
                    # Equality
                    where_clauses.append(f'"{col}" = ?')
                    params.append(cond)

        where_sql = ""
        if where_clauses:
            clause = " AND ".join(where_clauses)
            if mode == "include":
                where_sql = f"WHERE {clause}"
            elif mode == "exclude":
                where_sql = f"WHERE NOT ({clause})"
            else:
                conn.close()
                raise ValueError("mode must be 'include' or 'exclude'.")

        query = f'SELECT * FROM "{table_name}" {where_sql};'
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows


    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # For dict-like row access
        self.cursor = self.conn.cursor()

    def table_exists(self, table_name: str) -> bool:
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,),
        )
        return self.cursor.fetchone() is not None

    def get_table_columns(self, table_name: str) -> List[str]:
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        return [row["name"] for row in self.cursor.fetchall()]

    def create_table(self, table_name: str, columns: List[str]):
        # All columns as TEXT for now
        columns_def = ", ".join([f'"{col}" TEXT' for col in columns])
        self.cursor.execute(
            f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_def});'
        )
        self.conn.commit()

    def add_columns(self, table_name: str, new_columns: List[str]):
        for col in new_columns:
            self.cursor.execute(
                f'ALTER TABLE "{table_name}" ADD COLUMN "{col}" TEXT;'
            )
        self.conn.commit()

    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]], prevent_duplicates: bool = True):
        if not rows:
            return

        columns = list(rows[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        col_names = ", ".join([f'"{col}"' for col in columns])

        if prevent_duplicates and "id" in columns:
            # Only insert rows whose id is not already present
            existing_ids = set()
            self.cursor.execute(
                f'SELECT id FROM "{table_name}" WHERE id IS NOT NULL;'
            )
            existing_ids = {row["id"] for row in self.cursor.fetchall()}
            rows_to_insert = [row for row in rows if str(row.get("id")) not in existing_ids]
        else:
            rows_to_insert = rows

        for row in rows_to_insert:
            values = [str(row.get(col, "")) for col in columns]
            self.cursor.execute(
                f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders});',
                values,
            )
        self.conn.commit()

    def fetch_all(self, table_name: str) -> List[Dict[str, Any]]:
        self.cursor.execute(f'SELECT * FROM "{table_name}";')
        return [dict(row) for row in self.cursor.fetchall()]

    def close(self):
        self.conn.close()
