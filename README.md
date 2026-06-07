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
cd I:\BITS\SEM-3\NLP\Assignment
python -m venv .venv
. .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Optional packages
- `streamlit`: only if you want the UI
- `spacy` and `en_core_web_sm`: only if you want richer entity/triple extraction

Example optional install:
```powershell
python -m pip install streamlit
python -m pip install spacy
python -m spacy download en_core_web_sm
```

## LLM details
- Default model: `gpt2`
- This is a free open-source model from Hugging Face and is used locally
- Model weights are not included in `requirements.txt` or the repo
- The first run downloads the weights automatically into the Hugging Face cache

### Notes
- `gpt2` is free to run locally, but it is a basic model and not as strong as modern commercial LLMs
- If you want a different model, update `llm/answer.py` and install any extra dependencies required by that model

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

### 5. Optional Streamlit UI
```powershell
python -m pip install streamlit
streamlit run app.py
```
Then open the URL shown in the terminal.

## If Streamlit or spaCy cannot be installed
This repository is designed to work with the core backend even if the optional packages fail to install.
- `requirements.txt` contains the core packages needed for FastAPI, Neo4j, and the default LLM
- `streamlit` is not required unless you want the UI
- `spacy` is optional; a simple fallback extractor is already included

## Useful scripts
- `python prepare_data.py` — generate `data/org_passages.csv`
- `python build_index.py` — ingest passages into Neo4j
- `python evaluate.py` — run example queries against the backend
- `python scripts/run_demo.py` — offline demo mode for local QA without Neo4j

## Troubleshooting
- If `build_index.py` fails with connection refused, make sure `corporg` is started in Neo4j Desktop
- If auth fails, verify `NEO4J_PASSWORD` matches the Neo4j database password
- If `git` is not found, install Git for Windows and reopen PowerShell

## Recommended workflow for new team members
1. Clone the repo
2. Create a virtual environment and install `requirements.txt`
3. Start Neo4j Desktop and the `corporg` DB
4. Set environment variables
5. Run `python build_index.py`
6. Run `python -m uvicorn backend.main:app --reload --port 8000`
7. Use the API or optional Streamlit UI
