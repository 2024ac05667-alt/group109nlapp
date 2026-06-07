import os
import os
from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import csv
from kg.neo4j_client import Neo4jClient
from nl2cypher import translate_question_to_cypher
from llm.answer import generate_answer

# Try importing the richer extractor; if unavailable (no spaCy), provide a lightweight fallback
try:
    from kg.ingest import extract_and_ingest
except Exception:
    def extract_and_ingest(neo4j_client, text: str):
        # Very small heuristic extractor (mirrors ingest_via_bolt logic)
        parts = [p.strip() for p in text.split('.') if p.strip()]
        subj = None
        comp = None
        role = None
        manager = None
        dept = None
        for p in parts:
            if ' is the ' in p and ' at ' in p:
                try:
                    s, rest = p.split(' is the ', 1)
                    r, at, c = rest.rpartition(' at ')
                    subj = s.strip()
                    role = r.strip()
                    comp = c.strip()
                except Exception:
                    pass
            if ' reports to ' in p:
                try:
                    s, m = p.split(' reports to ', 1)
                    manager = m.strip()
                except Exception:
                    pass
            if ' works in the ' in p and ' department' in p:
                try:
                    s, rest = p.split(' works in the ', 1)
                    d = rest.replace(' department', '').strip()
                    dept = d
                except Exception:
                    pass

        if subj:
            neo4j_client.execute_write("MERGE (a:Entity {name: $s})", {"s": subj})
        if comp:
            neo4j_client.execute_write("MERGE (c:Company {name: $c})", {"c": comp})
        if subj and comp:
            neo4j_client.execute_write("MATCH (a:Entity {name:$s}), (c:Company {name:$c}) MERGE (a)-[:WORKS_AT]->(c)", {"s": subj, "c": comp})
        if subj and role:
            neo4j_client.execute_write("MERGE (r:Role {title:$role}) MERGE (a:Entity {name:$s}) MERGE (a)-[:HAS_ROLE]->(r)", {"s": subj, "role": role})
        if subj and manager:
            neo4j_client.execute_write("MERGE (m:Entity {name:$m}) MERGE (a:Entity {name:$s}) MERGE (a)-[:REPORTS_TO]->(m)", {"s": subj, "m": manager})
        if subj and dept:
            neo4j_client.execute_write("MERGE (d:Department {name:$d}) MERGE (a:Entity {name:$s}) MERGE (a)-[:IN_DEPARTMENT]->(d)", {"s": subj, "d": dept})

app = FastAPI(title="KG-Augmented Generative QA - Group 109")

static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
app.mount("/static", StaticFiles(directory=static_dir), name="static")

neo4j_client = Neo4jClient()


@app.get("/")
def index():
    return RedirectResponse(url="/static/index.html")


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    # expects a CSV with a column named 'text'
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    rows = []
    try:
        reader = csv.DictReader(text.splitlines())
        for r in reader:
            rows.append(r.get("text") or r.get("passage") or "")
    except Exception:
        rows = [text]

    count = 0
    for t in rows:
        if not t.strip():
            continue
        extract_and_ingest(neo4j_client, t)
        count += 1

    return {"ingested_passages": count}


@app.post("/nl2cypher")
async def nl2cypher(question: str = Form(...)):
    cypher = translate_question_to_cypher(neo4j_client, question)
    return {"cypher": cypher}


@app.api_route("/query", methods=["GET", "POST"])
async def query(question: str = Form(None), question_query: str = Query(None, alias="question")):
    text = question if question is not None else question_query
    if not text:
        return JSONResponse({"answer": "Question is required."}, status_code=400)

    cypher = translate_question_to_cypher(neo4j_client, text)
    if not cypher:
        return JSONResponse({"answer": "Could not translate question to graph query."}, status_code=400)

    records = neo4j_client.run_query(cypher)
    facts = []
    for r in records:
        facts.append(dict(r))

    answer = generate_answer(text, facts)
    return {"question": text, "cypher": cypher, "facts": facts, "answer": answer}
