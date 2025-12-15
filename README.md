# AI Data Analysis Agent (LangGraph + Streamlit)

This project is an end-to-end **agentic data analysis app** that allows users to upload **any CSV** and ask questions in natural language to get **data quality checks, aggregations, summary statistics, and visualizations**.  
Under the hood, it uses a **Planner → Router → Executor** architecture orchestrated with **LangGraph**, and a **Streamlit chat UI** to deliver results in a clean, user-friendly way.

---

## What the Project Delivers

### For Users (Product Outcomes)
- Upload a CSV and instantly see a **schema preview**
- Ask analysis questions and receive:
  - **Tables** (aggregations, rankings, summaries)
  - **Charts** (bar/line/scatter/hist)
  - **Data quality audit** (missing values, duplicates, dtypes)
- Works across different datasets without hardcoding column names

### For Developers (Engineering Outcomes)
- A structured and debuggable agent system that returns:
  - **Plan (AnalysisPlan JSON)**
  - **Confidence score**
  - **Explanation of what was executed**
  - **Artifacts** (`result_df` / `fig` / `schema`)
  - **Fail-safe errors** (no Streamlit crashes)

---

## End-to-End Workflow (How It Works)

### User Journey
1. User uploads a CSV in Streamlit
2. App runs a **preview-only flow** to display dataset schema
3. User asks a question such as:
   - “total revenue by region”
   - “top 5 products by sales”
   - “any missing values?”
   - “plot revenue by region”
   - “show growth of revenue”
4. Agent produces:
   - **Plan** (what it will do)
   - **Confidence** (how sure it is)
   - **Execution results** (table or chart)
   - **Explanation** (what ran)

### Agent Architecture
This is a deterministic “analytics copilot” agent with clear responsibilities:

- **DataLoader Node**: loads CSV into a DataFrame (with basic type coercion)
- **SchemaPreview Node**: builds schema preview payload
- **Planner Node**: infers intent + columns and generates an `AnalysisPlan`
- **Router**: selects the correct execution path based on `task_type`
- **Executor Node**: runs the requested computation / visualization
- **Response Builder**: packages results into one UI-ready payload
- **Memory Update**: stores `previous_plan` to support follow-up questions

---

## Agent Flow (LangGraph)

High-level pipeline:

> Add your LangGraph flow image here (recommended).
> Example:
> `> `<img width="565" height="1017" alt="image" src="https://github.com/user-attachments/assets/0dec07ea-9f14-47ce-8330-4e57aba1a0a3" />`

---

## Technologies Used

### Core Stack
- **Python** — core implementation
- **Pandas** — data loading, cleaning, aggregation, profiling
- **Streamlit** — web UI: file upload, chat interface, session state, rendering results

### Agent Workflow / Orchestration
- **LangGraph** — node-based workflow engine with conditional routing

### Data Modeling & Types
- **Pydantic** — validated `AnalysisPlan` schema
- **TypedDict / typing** — strongly-typed agent state

### Visualization
- **Matplotlib** — charts returned to the UI (`fig`)

### Supporting Tools
- **Regex (`re`)** — intent detection + column matching
- **os / tempfile** — safe local handling of uploaded files

---

## Techniques & Concepts Implemented

### 1) Heuristic Intent Classification
The planner detects user intent using keywords/patterns:
- **Visualization**: plot, chart, graph, growth, trend, line, bar, scatter, histogram
- **Data Quality**: missing, null, duplicate, dtype, audit, cleaning
- **Aggregation / KPIs**: total, sum, avg, mean, min, max, top, rank
- **Volatility**: std, standard deviation, volatility
- **Summary**: summary, describe, stats, distribution

This makes the system **fast, deterministic, and debuggable**.

### 2) Dynamic Column Inference (Dataset-Agnostic)
To support any dataset:
- Column name normalization (case/underscore/space tolerant)
- Token overlap scoring between question and column names
- Dtype-aware selection:
  - numeric columns are preferred as metrics
  - categorical columns are preferred for group-by
- Fallback logic when the question is ambiguous

### 3) Robust CSV Handling
Real-world CSVs often include messy data. The executor supports:
- numeric coercion for values like `18,000`, `$1,200`, `(300)`
- safe plotting with `__index__` fallback for growth/trend if no date column exists
- fail-safe error handling that returns structured errors instead of crashing the app

### 4) Stateful Follow-Up Questions
The system stores `previous_plan` so users can ask follow-ups like:
- “now plot it”
- “top 5 instead”
- “show std instead of sum”
without repeating the full context.

---

## Capabilities (What the Agent Can Do)

### 1) Schema Preview (on upload)
Returns:
- columns, dtypes
- row count
- missing %
- unique counts
- sample rows

### 2) Data Quality / Audit (`task_type="data_quality"`)
Example questions:
- “Any missing values?”
- “Any duplicates?”
- “Show dtypes”

Returns:
- missing percentages
- duplicate rows count
- dtype summary
- basic profiling payload

### 3) Aggregations 
Example questions:
- “Total revenue by region”
- “Average salary by department”
- “Top 5 products by sales”



### 4) Summary Statistics 
Example questions:
- “Describe sales”
- “Summary statistics”



### 5) Visualizations 
Example questions:
- “Plot revenue by region”
- “Show growth of revenue”
- “Scatter sales vs profit”
- “Histogram of revenue”



---

## Project Structure

`

Typical layout:
```text
analysis_agent/
├─ app.py
├─ graph/
│  ├─ __init__.py
│  └─ graph.py
├─ agent/
│  ├─ core/
│  │  └─ planner.py
│  ├─ execution/
│  │  └─ executor.py
│  └─ schema/
│     └─ models.py
├─ data/
├─ outputs/
└─ requirements.txt
```

## How to Run Locally

### 1) Create and activate a virtual environment
```bash
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
```
### 2) Install dependencies
```bash
pip install -r requirements.txt
```
### 3)Run the Streamlit app
```bash
streamlit run app.py
```
