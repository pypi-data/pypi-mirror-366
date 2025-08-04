# BenchLoop

**BenchLoop** is a Python library for managing, processing, and benchmarking datasets in SQLite databases—designed for AI pipelines, LLM prompt engineering, and dataset curation.

---

## 🚀 Features

- **Load & Update Data:** Ingest CSV, JSON, or Python dicts into SQLite with automatic table/column creation.
- **Flexible Filtering:** Query and filter rows with powerful, SQL-like conditions.
- **Prompt Execution:** Run prompts row-by-row, substitute variables, call LLMs (OpenAI), and store responses.
- **Dataset Export:** Export training datasets in JSONL (OpenAI "messages" or input/output format).
- **Benchmarking:** Compare AI responses vs. ground truth with exact and fuzzy match metrics.
- **Reproducible Loops:** Build scalable, iterative data workflows for AI/ML.

---

## 📦 Installation

BenchLoop is available on PyPI. Install it with:

```bash
pip install benchloop
```

> **Note:** You will also need the `openai` package for LLM prompt execution:
>
> ```bash
> pip install openai
> ```

---

## 🏁 Quickstart

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

## 📚 Documentation

- See the [full documentation](docs/benchloop.md) for API reference, advanced usage, and troubleshooting.
- Example/test script: [main.py](main.py)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Open an issue or submit a pull request on [GitHub](https://github.com/merlinaifoundation/benchloop).

---

## 📝 License

[MIT License](LICENSE)

---

**BenchLoop** makes dataset curation, prompt engineering, and benchmarking fast, reproducible, and robust for modern AI workflows.
