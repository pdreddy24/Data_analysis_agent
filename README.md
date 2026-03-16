# 🤖 Multi-Modal Data Analysis Agent

An **AI-powered multi-agent system** that performs automated **data analysis, visualization, and explanation** using modular intelligent agents.

The system orchestrates specialized agents for **planning, execution, visualization, memory, and natural language explanations**, enabling end-to-end **automated data analysis workflows**.

This project demonstrates how **multi-modal agents collaborate to interpret datasets, generate analysis code, execute pipelines, and produce insights automatically.**

---

# 🚀 Features

### 🧠 Multi-Agent Architecture

The system consists of specialized AI agents working together:

- **Planner Agent**
  - Interprets the user query
  - Generates a structured analysis plan

- **Code Generator Agent**
  - Converts the analysis plan into executable Python code

- **Execution Agent**
  - Runs generated code safely
  - Processes and analyzes datasets

- **Data Cleaning Agent**
  - Handles missing values and preprocessing

- **Visualization Agent**
  - Generates charts and graphical insights

- **Explanation Agent**
  - Converts results into human-readable insights

- **Memory Agent**
  - Maintains context and history for follow-up queries

---

# 🧩 Multimodal Capabilities

The system supports multiple forms of analytical reasoning:

- Structured Data Analysis (CSV datasets)
- Data Cleaning & Preprocessing
- Statistical Analysis
- Visualization Generation
- Natural Language Insights
- Interactive Query Handling

Users can **ask questions in natural language and receive analytical outputs with charts and explanations.**

---

# 🏗️ System Architecture

```
User Query
     │
     ▼
Planner Agent
     │
     ▼
Code Generator Agent
     │
     ▼
Execution Agent
     │
     ├── Data Cleaner
     ├── Data Analyzer
     └── Visualization Agent
     │
     ▼
Explanation Agent
     │
     ▼
Final Insights + Visualizations
```

---

# 📂 Project Structure

```
Data_analysis_agent/
│
├── agent/
│   ├── core/                # Planning and code generation logic
│   ├── execution/           # Data processing and execution pipeline
│   ├── explanation/         # Insight generation
│   ├── graph/               # Agent workflow graph
│   ├── memory/              # Agent memory management
│   ├── schema/              # Validation schemas
│   ├── visualization/       # Visualization logic
│   ├── preprocessing.py     # Data cleaning utilities
│   └── service.py           # Agent orchestration
│
├── tools/
│   └── data_loader.py       # Dataset loading utilities
│
├── data/
│   ├── sample_data.csv
│   ├── sample_data_2.csv
│   └── sample_data3.csv
│
├── prompts/
│   └── planner_prompt.txt   # Prompt template for planning agent
│
├── schemas/
│   └── plan_schema.py       # Plan validation schema
│
├── graph/
│   └── graph.py             # Agent workflow definition
│
├── app.py                   # Interactive application
├── main.py                  # Main execution script
├── requirements.txt         # Dependencies
└── README.md
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/your-username/Data_analysis_agent.git
cd Data_analysis_agent
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment:

Mac/Linux
```bash
source venv/bin/activate
```

Windows
```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Project

Run the main agent pipeline:

```bash
python main.py
```

Or run the interactive application:

```bash
python app.py
```

---

# 🧪 Example Query

Example input:

```
Analyze the dataset and show the correlation between sales and marketing spend.
```

The system will automatically:

1. Interpret the request
2. Generate a plan
3. Write analysis code
4. Execute the analysis
5. Generate visualizations
6. Provide explanations

Example output:

- Correlation analysis
- Visualization charts
- Natural language insights

---

# 🧠 Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib / Seaborn
- Multi-Agent AI Architecture
- Prompt-based Planning
- Schema Validation

---

# 🔬 Applications

This system can be used for:

- Automated Business Analytics
- AI Data Assistants
- Research Data Exploration
- Data Science Workflow Automation
- Intelligent BI Systems

---

# 📊 Future Improvements

- Integration with LLMs (GPT / Claude / Gemini)
- SQL database support
- Advanced multimodal inputs (images, dashboards)
- Integration with LangGraph / LangChain
- Interactive dashboards using Streamlit

---

# 🤝 Contributing

Contributions are welcome.

Steps:

1. Fork the repository
2. Create a new feature branch
3. Commit your changes
4. Submit a pull request

---

# 📜 License

This project is licensed under the **MIT License**.

---

# 👨‍💻 Author

Developed as a **Multi-Agent Data Analysis System for automated intelligent analytics workflows.**
