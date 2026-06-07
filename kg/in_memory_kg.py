import csv
from typing import List, Dict


class InMemoryKG:
    """Very small in-memory store to simulate passages for offline demos.

    API: `run_query(cypher, parameters)` returns list of dicts similar to Neo4jClient.
    The query parsing is intentionally tiny: it supports returning all passages
    or simple CONTAINS filtering for a `$term` parameter.
    """

    def __init__(self):
        self.passages: List[Dict] = []

    def ingest_passage(self, pid: str, text: str):
        self.passages.append({"id": pid, "text": text})

    def bulk_load_csv(self, path: str, text_field: str = 'text'):
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, r in enumerate(reader):
                txt = r.get(text_field) or r.get('passage') or r.get('text', '')
                self.ingest_passage(str(i), txt)

    def run_query(self, cypher: str, parameters: Dict = None):
        parameters = parameters or {}
        # support: MATCH (p:Passage) RETURN p LIMIT N  -> return first N passages
        if 'MATCH' in cypher and 'Passage' in cypher:
            term = None
            # very small parser: look for CONTAINS $term or 'CONTAINS' literal
            if 'CONTAINS' in cypher and '$' in cypher:
                # parameter key guess
                for k in parameters:
                    if isinstance(parameters[k], str):
                        term = parameters[k]
                        break
            elif 'CONTAINS' in cypher:
                # attempt to extract literal
                parts = cypher.split('CONTAINS')
                if len(parts) > 1:
                    lit = parts[1].strip().strip('"').strip("'")
                    term = lit

            results = []
            for p in self.passages:
                if term is None or (term and term.lower() in p['text'].lower()):
                    results.append({'p': p})
            return results

        # fallback: return empty list
        return []
