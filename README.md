# KG-Augmented Generative QA — Group 109

This project implements a minimal Knowledge Graph-augmented generative QA prototype using Neo4j and a free generative model (`gpt2`).

Prerequisites:
- Python 3.9+
- Neo4j running locally or accessible (set `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` env vars)

Install:
```bash
python -m pip install -r requirements.txt
# spaCy is optional; fallback extractor is included and is sufficient for the lab.
# If you want spaCy for richer extraction, install it manually and download a model:
# python -m pip install spacy
# python -m spacy download en_core_web_sm
```

Optional: run the app with Streamlit if your environment supports it:
```bash
set NEO4J_URI=bolt://localhost:7687
set NEO4J_USER=neo4j
set NEO4J_PASSWORD=yourpassword
python -m pip install streamlit
streamlit run app.py
```
Then open the Streamlit URL shown in the terminal, usually http://127.0.0.1:8501.

If Streamlit cannot be installed in the lab, use the FastAPI backend directly instead.

Support scripts:
```bash
python prepare_data.py   # generate data/org_passages.csv
python build_index.py    # ingest data into Neo4j via HTTP
python evaluate.py       # run sample question evaluation
```

Alternative API mode (FastAPI + uvicorn):
```bash
set NEO4J_URI=bolt://localhost:7687
set NEO4J_USER=neo4j
set NEO4J_PASSWORD=yourpassword
uvicorn backend.main:app --reload --port 8000
```
This API mode is backend-only and does not serve a separate HTML frontend.

Note: The previous single-file Colab notebook has been removed from the repository.
Use the scripts in the `scripts/` folder for dataset generation and ingestion instead.

Temporary cleanup: removed notebook files and Python cache files to reduce repository size.

If you need the notebook restored, it's available on request.

Removed files:
- `KG_QA_Colab_single.ipynb`
- `KG_QA_Colab.ipynb`
- Python cache files
- `.venv` (left in place if removal may break local environment)


Usage:
- Run the Streamlit UI with `streamlit run app.py`.
- Upload a CSV with a `text` column to ingest passages into Neo4j.
- Ask a natural language question and review the translated Cypher, retrieved facts, and generated answer.
- If you use FastAPI mode, it is API-only and does not provide the Streamlit UI.

Notes and next steps:
- The NL→Cypher component is rule-based as a starting point; for production you'd use a stronger semantic parser or an LLM translator.
- Entity/triple extraction uses a simple SVO heuristic; consider OpenIE or supervised models for higher quality.
