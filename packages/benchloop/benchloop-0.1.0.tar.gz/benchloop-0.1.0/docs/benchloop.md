# BenchLoop Library Documentation

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Project Structure](#project-structure)
4. [Quickstart](#quickstart)
5. [API Reference](#api-reference)
    - [load_table](#load_table)
    - [filter_rows](#filter_rows)
    - [execute_prompt_on_table](#execute_prompt_on_table)
    - [export_training_dataset](#export_training_dataset)
    - [benchmark_responses](#benchmark_responses)
6. [Advanced Usage](#advanced-usage)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Introduction

**BenchLoop** is a Python library for managing, processing, and benchmarking datasets in SQLite databases, designed for AI pipelines, LLM prompt engineering, and dataset curation. It enables you to:
- Load and update structured data in SQLite.
- Run prompts row-by-row, substitute variables, and store LLM responses.
- Filter, export, and benchmark datasets with ease.
- Build reproducible, scalable data loops for AI/ML workflows.

---

## Installation

**Requirements:**
- Python 3.7+
- Standard libraries: `sqlite3`, `csv`, `json`, `os`, `difflib`
- For LLM calls: `openai` (install via `pip install openai`)

**Install BenchLoop:**

```bash
pip install benchloop
pip install openai  # For LLM prompt execution
```

---

## Project Structure

```
benchloop/
├── __init__.py
├── loader.py
├── db_manager.py
├── prompt_runner.py
├── dataset_exporter.py
├── benchmarker.py
docs/
└── benchloop.md
main.py
```

- **loader.py**: Data ingestion (CSV, JSON, dicts) into SQLite.
- **db_manager.py**: Core DB operations and flexible filtering.
- **prompt_runner.py**: Row-wise prompt execution and LLM integration.
- **dataset_exporter.py**: Export datasets for training (JSONL, etc.).
- **benchmarker.py**: Benchmarking AI responses vs. ground truth.
- **main.py**: Example/test script for all features.

---

## Quickstart

```python
from benchloop.loader import load_table
from benchloop.prompt_runner import execute_prompt_on_table
from benchloop.dataset_exporter import export_training_dataset
from benchloop.benchmarker import benchmark_responses

# 1. Load data
load_table(
    table_name="products",
    data_source=[{"id": 1, "name": "Zapato", "price": "50"}],
    db_path="mydb.sqlite"
)

# 2. Run prompts and store LLM responses
execute_prompt_on_table(
    table_name="products",
    prompt_template="Describe the product {name} that costs {price} dollars.",
    columns_variables=["name", "price"],
    result_mapping={"response": "llm_response"},
    db_path="mydb.sqlite",
    model="gpt-4o",
    api_key="sk-...",
)

# 3. Export dataset for training
export_training_dataset(
    table_name="products",
    prompt_template="Describe the product {name} that costs {price} dollars.",
    response_column="llm_response",
    output_file="dataset.jsonl",
    db_path="mydb.sqlite",
    format="messages"
)

# 4. Benchmark responses
benchmark_responses(
    table_name="products",
    column_ai="llm_response",
    column_ground_truth="ground_truth",
    db_path="mydb.sqlite",
    benchmark_tag=None
)
```

---

## API Reference

### load_table

**Purpose:**  
Load structured data into an SQLite table from CSV, JSON, or a list of dicts.  
**Location:** `benchloop/loader.py`

**Signature:**
```python
load_table(table_name: str, data_source: Union[str, List[Dict]], db_path: str)
```

**Parameters:**
- `table_name`: Name of the table.
- `data_source`: Path to CSV/JSON file or a list of dicts.
- `db_path`: Path to the SQLite database.

**Features:**
- Auto-creates table and columns as needed.
- Adds new columns on the fly.
- Prevents duplicate insertions (if `id` is present).

**Example:**
```python
load_table("mytable", "data.csv", "mydb.sqlite")
```

---

### filter_rows

**Purpose:**  
Flexible filtering of rows with support for operators and include/exclude modes.  
**Location:** `benchloop/db_manager.py`

**Signature:**
```python
DBManager.filter_rows(table_name: str, filters: dict, mode: str, db_path: str) -> list
```

**Parameters:**
- `table_name`: Table to filter.
- `filters`: Dict of conditions (supports `=`, `!=`, `>`, `<`, `contains`, `startswith`, `IN`).
- `mode`: `'include'` or `'exclude'`.
- `db_path`: Path to the SQLite database.

**Example:**
```python
rows = DBManager.filter_rows("mytable", {"price": {">": 100}}, "include", "mydb.sqlite")
```

---

### execute_prompt_on_table

**Purpose:**  
Run prompts row-by-row, substitute variables, call LLM, and store responses.  
**Location:** `benchloop/prompt_runner.py`

**Signature:**
```python
execute_prompt_on_table(
    table_name: str,
    prompt_template: str,
    columns_variables: List[str],
    result_mapping: Dict[str, str],
    db_path: str,
    filters: Optional[Dict] = None,
    limit: Optional[int] = None,
    model: str = "gpt-4o",
    api_key: str = ""
)
```

**Parameters:**
- `table_name`: Table to process.
- `prompt_template`: Prompt with `{}` placeholders.
- `columns_variables`: List of columns to substitute.
- `result_mapping`: Dict mapping LLM response fields to DB columns.
- `db_path`: Path to the SQLite database.
- `filters`: Optional row filters.
- `limit`: Max rows to process.
- `model`: LLM model name.
- `api_key`: OpenAI API key.

**Example:**
```python
execute_prompt_on_table(
    "products",
    "Describe {name}",
    ["name"],
    {"response": "llm_response"},
    "mydb.sqlite",
    model="gpt-4o",
    api_key="sk-..."
)
```

---

### export_training_dataset

**Purpose:**  
Export a JSONL dataset for training, with prompt/response pairs.  
**Location:** `benchloop/dataset_exporter.py`

**Signature:**
```python
export_training_dataset(
    table_name: str,
    prompt_template: str,
    response_column: str,
    output_file: str,
    db_path: str,
    filters: Optional[Dict] = None,
    format: str = "messages"
)
```

**Parameters:**
- `table_name`: Table to export from.
- `prompt_template`: Prompt template with placeholders.
- `response_column`: Column with LLM response.
- `output_file`: Output JSONL file path.
- `db_path`: Path to the SQLite database.
- `filters`: Optional row filters.
- `format`: "messages" (OpenAI style) or "input/output".

**Example:**
```python
export_training_dataset(
    "products",
    "Describe {name}",
    "llm_response",
    "dataset.jsonl",
    "mydb.sqlite"
)
```

---

### benchmark_responses

**Purpose:**  
Compare AI responses vs. ground truth and compute metrics.  
**Location:** `benchloop/benchmarker.py`

**Signature:**
```python
benchmark_responses(
    table_name: str,
    column_ai: str,
    column_ground_truth: str,
    db_path: str,
    benchmark_tag: Optional[str] = None,
    benchmark_column: str = "benchmark",
    similarity_threshold: float = 0.9
) -> Dict
```

**Parameters:**
- `table_name`: Table to benchmark.
- `column_ai`: Column with AI responses.
- `column_ground_truth`: Column with ground truth.
- `db_path`: Path to the SQLite database.
- `benchmark_tag`: Only include rows with this tag.
- `benchmark_column`: Name of the tag column.
- `similarity_threshold`: Fuzzy match threshold.

**Example:**
```python
metrics = benchmark_responses(
    "products",
    "llm_response",
    "ground_truth",
    "mydb.sqlite",
    benchmark_tag="PrecioTest"
)
```

---

## Advanced Usage

- **Custom Prompt Templates:** Use any columns in your prompt template.
- **Chaining:** Use filter_rows to select rows, then run prompts or export.
- **Multiple Benchmarks:** Use the `benchmark` column to tag and compare different subsets.
- **Export Formats:** Use `format="input/output"` for simple datasets, or `"messages"` for OpenAI-style.

---

## Best Practices

- Always use unique `id` fields for deduplication.
- Use filters to avoid re-processing already-annotated rows.
- Store ground truth in a dedicated column for benchmarking.
- Version your datasets and keep track of prompt templates used.

---

## Troubleshooting

- **No rows exported?** Check your filters and that the response column is populated.
- **Prompt errors?** Ensure all variables in the template exist as columns.
- **Benchmark returns 0 rows?** Check the benchmark tag and that ground truth is present.

---

## FAQ

**Q: Can I use this with any LLM provider?**  
A: The prompt runner is designed for OpenAI, but you can adapt it for other APIs.

**Q: How do I add new columns?**  
A: Just include new keys in your data dicts or CSV/JSON files; columns are added automatically.

**Q: Can I export only a subset of rows?**  
A: Yes, use the `filters` parameter in `export_training_dataset`.

**Q: How do I benchmark only a specific subset?**  
A: Use the `benchmark_tag` parameter in `benchmark_responses`.

---

**BenchLoop** is designed to make dataset curation, prompt engineering, and benchmarking fast, reproducible, and robust.  
For more examples, see `main.py` or open an issue on the project repository.
