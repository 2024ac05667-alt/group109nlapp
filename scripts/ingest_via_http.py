"""
Ingest dataset into Neo4j using HTTP transactional endpoint (no external driver required).
Set environment variables or edit the NEO4J_URI/USER/PASSWORD below.
"""
import os
import csv
import json
import base64
from urllib.request import Request, urlopen


NEO4J_HTTP = os.environ.get("NEO4J_HTTP", "http://127.0.0.1:7474")
NEO4J_DB = os.environ.get("NEO4J_DATABASE", "corporg")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "12345678")


def cypher_request(statements):
    url = f"{NEO4J_HTTP}/db/{NEO4J_DB}/tx/commit"
    payload = json.dumps({"statements": statements}).encode("utf-8")
    auth = base64.b64encode(f"{NEO4J_USER}:{NEO4J_PASSWORD}".encode()).decode()
    req = Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Content-Type", "application/json")
    resp = urlopen(req)
    return json.load(resp)


def ingest_row(text):
    # Simple pattern extraction for our synthetic data format
    # Examples produced by generator: "Alex Smith is the CTO at Apex Systems. Alex Smith reports to Jamie Doe. Alex Smith works in the Engineering department."
    parts = [p.strip() for p in text.split('.') if p.strip()]
    subj = None
    comp = None
    role = None
    manager = None
    dept = None
    for p in parts:
        if ' is the ' in p and ' at ' in p:
            # e.g., 'Alex Smith is the CTO at Apex Systems'
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

    statements = []
    params = {}
    if subj:
        statements.append({
            "statement": "MERGE (a:Entity {name: $s}) RETURN a.name",
            "parameters": {"s": subj},
        })
    if comp:
        statements.append({
            "statement": "MERGE (c:Company {name: $c}) RETURN c.name",
            "parameters": {"c": comp},
        })
    if subj and comp:
        statements.append({
            "statement": "MATCH (a:Entity {name:$s}), (c:Company {name:$c}) MERGE (a)-[:WORKS_AT]->(c)",
            "parameters": {"s": subj, "c": comp},
        })
    if subj and role:
        statements.append({
            "statement": "MERGE (r:Role {title:$role}) MERGE (a:Entity {name:$s}) MERGE (a)-[:HAS_ROLE]->(r)",
            "parameters": {"s": subj, "role": role},
        })
    if subj and manager:
        statements.append({
            "statement": "MERGE (m:Entity {name:$m}) MERGE (a:Entity {name:$s}) MERGE (a)-[:REPORTS_TO]->(m)",
            "parameters": {"s": subj, "m": manager},
        })
    if subj and dept:
        statements.append({
            "statement": "MERGE (d:Department {name:$d}) MERGE (a:Entity {name:$s}) MERGE (a)-[:IN_DEPARTMENT]->(d)",
            "parameters": {"s": subj, "d": dept},
        })

    if statements:
        return cypher_request(statements)
    return None


def ingest_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        n = 0
        for r in reader:
            text = r.get('text') or r.get('passage') or ''
            if text:
                try:
                    ingest_row(text)
                except Exception as e:
                    print('Ingestion stopped: could not reach Neo4j HTTP endpoint or error occurred.')
                    print('Error:', e)
                    return
                n += 1
    print(f"Ingested {n} rows via HTTP to {NEO4J_HTTP} (db={NEO4J_DB})")


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    data_path = os.path.normpath(os.path.join(here, '..', 'data', 'org_passages.csv'))
    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}")
    else:
        ingest_file(data_path)
