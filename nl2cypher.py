import re

def translate_question_to_cypher(neo4j_client, question: str):
    q = question.lower().strip()
    # naive entity extraction: look for quoted spans or Capitalized words
    ents = re.findall(r'"([^"]+)"|\b([A-Z][a-zA-Z0-9_\-]+(?:\s+[A-Z][a-zA-Z0-9_\-]+)*)', question)
    found = [t[0] or t[1] for t in ents if (t[0] or t[1])]

    tokens = q.split()
    # If question asks about relation between two entities
    if len(found) >= 2:
        a = found[0]
        b = found[1]
        cypher = (
            "MATCH (a:Entity {name: $a})-[r]->(b:Entity {name: $b}) RETURN a.name AS subject, type(r) AS rel, b.name AS object, r.type AS relprop"
        )
        return cypher.replace("$a", '"' + a + '"').replace("$b", '"' + b + '"')

    # fallback: search for nodes that mention tokens and return 1-hop neighbors
    # build a simple fulltext match on name
    keywords = [t for t in tokens if len(t) > 3]
    if keywords:
        term = " ".join(keywords[:4])
        cypher = (
            "MATCH (n:Entity) WHERE toLower(n.name) CONTAINS $term "
            "OPTIONAL MATCH (n)-[r]->(m:Entity) RETURN n.name AS subject, type(r) AS rel, m.name AS object LIMIT 50"
        )
        return cypher.replace("$term", '"' + term + '"')

    return None
