import sqlite3
from difflib import SequenceMatcher
from typing import Optional, Dict

def benchmark_responses(
    table_name: str,
    column_ai: str,
    column_ground_truth: str,
    db_path: str,
    benchmark_tag: Optional[str] = None,
    benchmark_column: str = "benchmark",
    similarity_threshold: float = 0.9
) -> Dict:
    """
    Compare AI-generated responses vs Ground Truth in a table and compute metrics.

    Parameters:
        table_name (str): Name of the table to benchmark.
        column_ai (str): Column with AI-generated responses.
        column_ground_truth (str): Column with Ground Truth values.
        db_path (str): Path to the SQLite database file.
        benchmark_tag (Optional[str]): Only include rows where benchmark_column == benchmark_tag.
        benchmark_column (str): Name of the benchmark tag column (default: "benchmark").
        similarity_threshold (float): Threshold for fuzzy match (default: 0.9).

    Returns:
        Dict: Metrics dictionary with counts and accuracies.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check columns exist
    cursor.execute(f"PRAGMA table_info({table_name});")
    table_columns = {row["name"] for row in cursor.fetchall()}
    for col in [column_ai, column_ground_truth]:
        if col not in table_columns:
            conn.close()
            raise ValueError(f"Column '{col}' does not exist in table '{table_name}'.")
    if benchmark_tag is not None and benchmark_column not in table_columns:
        conn.close()
        raise ValueError(f"Benchmark column '{benchmark_column}' does not exist in table '{table_name}'.")

    # Build WHERE clause
    where_clauses = [f'"{column_ground_truth}" IS NOT NULL']
    params = []
    if benchmark_tag is not None:
        where_clauses.append(f'"{benchmark_column}" = ?')
        params.append(benchmark_tag)
    where_sql = "WHERE " + " AND ".join(where_clauses)

    query = f'SELECT "{column_ai}", "{column_ground_truth}" FROM "{table_name}" {where_sql};'
    cursor.execute(query, params)
    rows = cursor.fetchall()

    if not rows:
        print("Warning: No rows found for benchmarking with the given criteria.")
        conn.close()
        return {
            "total": 0,
            "exact_matches": 0,
            "similarity_above_90": 0,
            "exact_match_accuracy": 0.0,
            "fuzzy_match_accuracy": 0.0
        }

    total = 0
    exact_matches = 0
    similarity_above_90 = 0

    for row in rows:
        ai_resp = row[column_ai]
        gt_resp = row[column_ground_truth]
        if ai_resp is None or gt_resp is None:
            continue
        total += 1
        ai_str = str(ai_resp).strip().lower()
        gt_str = str(gt_resp).strip().lower()
        if ai_str == gt_str:
            exact_matches += 1
        ratio = SequenceMatcher(None, ai_str, gt_str).ratio()
        if ratio >= similarity_threshold:
            similarity_above_90 += 1

    exact_acc = exact_matches / total if total else 0.0
    fuzzy_acc = similarity_above_90 / total if total else 0.0

    print(f"Total Samples: {total}")
    print(f"Exact Matches: {exact_matches} ({exact_acc:.2%})")
    print(f"Similarity > {int(similarity_threshold*100)}%: {similarity_above_90} ({fuzzy_acc:.2%})")

    conn.close()
    return {
        "total": total,
        "exact_matches": exact_matches,
        "similarity_above_90": similarity_above_90,
        "exact_match_accuracy": exact_acc,
        "fuzzy_match_accuracy": fuzzy_acc
    }
