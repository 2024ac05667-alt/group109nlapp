import os
import csv
import re
from kg.neo4j_client import Neo4jClient


def ingest_row_bolt(neo4j_client, text: str):
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


def ingest_file(path):
    client = Neo4jClient()
    n = 0
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            text = r.get('text') or ''
            if text:
                ingest_row_bolt(client, text)
                n += 1
    print(f'Ingested {n} rows via bolt to {os.environ.get("NEO4J_URI")}')


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    data_path = os.path.normpath(os.path.join(here, '..', 'data', 'org_passages.csv'))
    if not os.path.exists(data_path):
        print('Data file not found:', data_path)
    else:
        ingest_file(data_path)
