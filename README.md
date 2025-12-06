# 🧠 Natural Language to Hive Query Assistant

A production-style **Natural Language → HiveSQL Query Assistant** that enables users to query large datasets stored in **Apache Hive** using plain English.  
The system uses **LLMs for query generation**, validates queries using Hive’s execution planner, and safely executes the best SQL candidate.

---

## ✨ Key Features

- Natural Language → HiveSQL conversion  
- Multi-LLM candidate SQL generation (Gemini + DeepSeek)  
- Automatic SQL validation using `EXPLAIN`  
- Query ranking and best-SQL selection  
- Safe execution on Apache Hive (LIMIT enforcement, non-destructive queries)  
- Dockerized Hive backend  
- CLI + Web UI support  
- Modular and extensible architecture  

---

## 🏗️ System Architecture

User (Natural Language)
↓
Frontend / CLI
↓
Prompt Builder + Schema Injection
↓
LLM Translators (Gemini, DeepSeek)
↓
Candidate SQL Queries
↓
Comparator (EXPLAIN + Scoring)
↓
Best SQL Query
↓
Hive Execution (HiveServer2)
↓
Query Results

---


---

## 🧠 LLMs Used

| Model | Platform | Role |
|------|--------|------|
| Gemini 2.5 Flash | Google GenAI | Primary NL → SQL generation |
| DeepSeek-V3.2 | Hugging Face Inference | Secondary SQL candidate |

Using multiple LLMs improves query reliability and reduces hallucinations.

---

⚙️ Setup Instructions

1️⃣ Environment Setup

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2️⃣ Run Hive Using Docker

docker run -d \
  -p 10000:10000 \
  -p 10002:10002 \
  --name hive4 \
  apache/hive:4.0.0


Verify:

docker ps

3️⃣ Load Data into Hive
python app/generate_sales_data.py
docker cp data/sales_full.csv hive4:/tmp/sales_full.csv


Inside Hive:

CREATE DATABASE nl2hive_demo;
USE nl2hive_demo;

CREATE TABLE sales (
  product_id STRING,
  price DOUBLE,
  quantity INT,
  sale_date STRING
);

LOAD DATA LOCAL INPATH '/tmp/sales_full.csv' INTO TABLE sales;

🔐 Environment Variables

export GOOGLE_GENAI_API_KEY="your_gemini_key"
export HF_TOKEN="your_huggingface_token"

---

▶️ Running the Project

CLI Mode
python -m app.main --nl "Top products by revenue in the demo sales table"

Web UI
export FLASK_APP=app.webapp
flask run
