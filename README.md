# KG-Augmented Generative QA — Group 109

This project is a lightweight Knowledge Graph-augmented generative QA prototype.
It ingests passages into a Neo4j graph, translates simple natural-language questions into Cypher, retrieves supporting facts, and generates an answer with a local open-source LLM.

## What is included
- FastAPI backend in `backend/main.py`
- Optional Streamlit UI in `backend/streamlit_app.py`
- Neo4j helper code in `kg/neo4j_client.py`
- Rule-based NL→Cypher translator in `nl2cypher.py`
- `scripts/` for data prep and ingestion
- Default local LLM integration via `llm/answer.py`

## Requirements
- Python 3.9 or newer
- Neo4j Desktop or another running Neo4j instance for full KG mode
- Internet access the first time the model is downloaded

### Install Python dependencies
```powershell
cd I:\BITS\Assignment
python -m venv .venv
. .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```


## LLM details
- Default model: `gpt2`
- This is a free open-source model from Hugging Face and is used locally
- Model weights are not included in `requirements.txt` or the repo
- The first run downloads the weights automatically into the Hugging Face cache


## Neo4j setup
### Local Neo4j Desktop
1. Open Neo4j Desktop
2. Start the local instance and the `corporg` database
3. Confirm the Bolt URI is `bolt://127.0.0.1:7687`
4. Use `neo4j` as username and your password

### Environment variables
Set these before running ingestion or the backend:
```powershell
$env:NEO4J_URI='bolt://127.0.0.1:7687'
$env:NEO4J_USER='neo4j'
$env:NEO4J_PASSWORD='12345678'
$env:NEO4J_DATABASE='corporg'
```

## Run the project
### 1. Prepare data
```powershell
python prepare_data.py
```

### 2. Ingest into Neo4j
```powershell
python build_index.py
```

### 3. Start the FastAPI backend
```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

### 4. Query the API
```powershell
curl "http://127.0.0.1:8000/query?question=Who%20is%20the%20CEO%20of%20the%20company%3F"
```

### 5.  Streamlit UI
```powershell
streamlit run app.py
```
Then open the URL shown in the terminal.

## Useful scripts
- `python prepare_data.py` — generate `data/org_passages.csv`
- `python build_index.py` — ingest passages into Neo4j
- `python evaluatcde.py` — run example queries against the backend
- `python scripts/run_demo.py` — offline demo mode for local QA without Neo4j

## Recommended workflow 
1. Clone the repo
2. Create a virtual environment and install `requirements.txt`
3. Start Neo4j Desktop and the `corporg` DB
4. Set environment variables
5. Run `python build_index.py`
6. Run `python -m uvicorn backend.main:app --reload --port 8000`
7. Other Terminal Set environment variables and Run `streamlit run app.py`
