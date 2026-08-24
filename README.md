# 📊 Data Analysis Agent

A conversational data analysis agent that lets you upload a CSV and ask questions about it in plain English — "what's total revenue by region?", "any duplicate rows?", "plot units sold over time" — and get back a computed table, a chart, or a data-quality report. The question-to-analysis pipeline is orchestrated as a small [LangGraph](https://github.com/langchain-ai/langgraph) state machine, with a rule-based planner that maps natural-language questions onto a deterministic, typed analysis plan (no LLM call, no hallucinated numbers).

The agent ships with two front ends:
- A **Streamlit chat UI** (`app.py`) for interactive, multi-turn analysis.
- A **CLI** (`main.py`) for quick terminal-based exploration.

## Features

- **Natural-language querying** — ask for aggregations, top-K rankings, summaries, data-quality checks, and charts without writing pandas code.
- **Automatic column resolution** — matches words in your question ("by region", "total revenue") to the closest matching dataframe columns, with numeric/categorical awareness.
- **Automatic type cleanup** — coerces messy numeric-looking strings (`"$18,000"`, `"(300)"`, `"45%"`) into real numbers before aggregating or plotting.
- **Multiple task types** — aggregation (sum/mean/min/max/count/std), top-K ranking, statistical summaries, data-quality audits (duplicates, missing values, dtypes), and visualizations (bar, line, scatter, histogram).
- **Follow-up awareness** — reuses the previous analysis plan as a starting point for things like "how volatile is that?" after an earlier aggregation.
- **Confidence scoring** — every response returns a confidence score so you can gauge how directly the question mapped to an analysis.
- **Graph-based orchestration** — the Streamlit app runs on an explicit LangGraph graph (load → route → plan/preview → execute → respond) that you can visualize from the UI's Developer mode.

## How it works

Both entry points funnel through the same core logic:

1. **Load** — the CSV is read into a pandas DataFrame and numeric-looking text columns are cleaned up.
2. **Plan** — `agent/core/planner.py` inspects the question with keyword and column-matching heuristics and produces a typed `AnalysisPlan` (task type, metrics, group-by columns, aggregation, chart type, etc.). No LLM is involved in this step, so plans are fast, deterministic, and reproducible.
3. **Execute** — `agent/execution/executor.py` runs the plan against the DataFrame and returns either a result table or a matplotlib figure.
4. **Respond** — the result, an explanation string, and a confidence score are bundled together for the UI, and the plan is stored as "previous plan" so follow-up questions can build on it.

The Streamlit app (`app.py`) wraps this in a LangGraph `StateGraph` (defined in `graph/graph.py`) with explicit nodes and conditional routing:

```
START → data_loader ─┬─(error)──────────────→ respond
                      ├─(preview_only)───────→ schema_preview → END
                      └─(else)───────────────→ planner ─┬─(error)→ respond
                                                          └─(else) → exec → respond
                                                                              ↓
                                                                       memory_update → END
```

Toggle **Developer mode** in the sidebar to render this graph (via `draw_mermaid_png`/`draw_mermaid`) directly in the app.

## Project structure

```
Data_analysis_agent-main/
├── app.py                       # Streamlit chat UI (LangGraph-backed)
├── main.py                      # CLI entry point (agent.service-backed)
├── graph/
│   ├── graph.py                 # LangGraph StateGraph: nodes + routing used by app.py
│   └── __init__.py              # exports the compiled `app` graph
├── agent/
│   ├── service.py                # run_analysis(): plan -> execute -> respond (used by main.py)
│   ├── core/
│   │   ├── planner.py             # rule-based question -> AnalysisPlan
│   │   └── router.py              # post-execution retry/route logic
│   ├── execution/
│   │   └── executor.py            # runs an AnalysisPlan against a DataFrame
│   ├── schema/
│   │   ├── models.py              # AnalysisPlan pydantic model
│   │   └── state.py                # AgentState TypedDict
│   └── ...                        # additional in-progress modules (see Notes below)
├── schemas/plan_schema.py        # standalone/alternate AnalysisPlan schema
├── tools/data_loader.py          # standalone CSV/Parquet loader + profiler
├── prompts/planner_prompt.txt    # prompt template for an LLM-based planner variant
├── data/                         # sample CSVs to try the agent with
├── requirements.txt
└── .devcontainer/                # one-click GitHub Codespaces / dev container setup
```

## Getting started

### Prerequisites
- Python 3.11+ (the dev container uses `python:3.11-bookworm`)
- pip

### Installation

```bash
git clone <this-repo-url>
cd Data_analysis_agent-main
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the Streamlit app

```bash
streamlit run app.py
```

Then, in the browser:
1. Upload a CSV (or use one of the files in `data/`).
2. Expand **Dataset schema preview** to see column types, missing values, and sample rows.
3. Ask a question in the chat box, e.g. `total revenue by region` or `plot units_sold over time`.
4. Use the **Show plan/debug** and **Show schema output** toggles to inspect what the agent computed under the hood.

### Run the CLI

```bash
python main.py
```

You'll be prompted for a dataset path and then can ask questions in a loop (type `exit` to quit).

## Example questions

Using `data/sample_data.csv` (`transaction_id, product_category, region, units_sold, revenue_usd`):

- `total revenue by region`
- `top 5 product categories by units sold`
- `average revenue`
- `any duplicate rows or missing values?`
- `plot revenue by region`
- `how volatile is revenue by region?` (as a follow-up — reuses the previous plan)

## Sample data

Three example CSVs are included under `data/`:
- `sample_data.csv` — sales transactions by product category and region
- `sample_data_2.csv` — daily stock price data by ticker/sector
- `sample_data3.csv` — a messier transactions file (extra whitespace in headers, currency-formatted numbers) useful for exercising the automatic type-cleanup logic

## Notes on project layout

This repository contains a couple of parallel/experimental modules that aren't wired into the active `app.py` / `main.py` pipeline yet, kept around for ongoing development:
- `agent/core/interpreter.py` — an LLM-based (LangChain + `ChatOpenAI`) explanation generator, an alternative to the current template-based `explanation` string. Wiring it in would require an `OPENAI_API_KEY`.
- `agent/execution/analyzer.py`, `cleaner.py`, `execute_helpers.py`, `agent/preprocessing.py`, `agent/visualization/visualizer.py`, `agent/explanation/explainer.py`, `agent/memory/memory.py`, `agent/schema/validator.py`, `agent/schema/capabilities.py`, `agent/core/{code_generator,question_suggester,followup_detector}.py`, `schemas/plan_schema.py`, and `tools/data_loader.py` — standalone building blocks (data cleaning, capability inference, follow-up detection, an alternate plan schema, a Parquet-aware loader, etc.) for features that aren't yet called from the live graph or CLI flow.

The currently active pipeline for both `app.py` and `main.py` is fully deterministic (no API key required): questions are matched to plans via keyword/column heuristics in `agent/core/planner.py`, and plans are executed with pandas/matplotlib in `agent/execution/executor.py` (or `graph/graph.py`'s nodes, which wrap the same planner/executor functions).

## License

MIT — see [LICENSE](LICENSE).

