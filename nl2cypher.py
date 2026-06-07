import re


def _normalize_name(text: str) -> str:
    return text.strip().strip('"').strip("'")


def translate_question_to_cypher(neo4j_client, question: str):
    q = question.lower().strip()
    quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', question)
    if quoted:
        quoted_terms = [t[0] or t[1] for t in quoted if (t[0] or t[1])]
    else:
        quoted_terms = []

    # Named entity extraction for capitalized names and companies
    ents = re.findall(r'\b([A-Z][a-zA-Z0-9_\-]+(?:\s+[A-Z][a-zA-Z0-9_\-]+)*)', question)
    found = [t for t in ents if t.lower() not in {'who', 'what', 'when', 'where', 'is', 'the', 'of', 'at', 'in', 'does', 'does', 'a', 'an', 'and'}]

    # department query: "works in the Legal department"
    dept_match = re.search(r'works in the ([A-Za-z ]+) department', q)
    if dept_match:
        dept = dept_match.group(1).strip().title()
        return (
            "MATCH (e:Entity)-[:IN_DEPARTMENT]->(d:Department {name: \"" + dept + "\"}) "
            "RETURN e.name AS subject, 'IN_DEPARTMENT' AS rel, d.name AS object LIMIT 100"
        )

    # reports-to query
    reports_match = re.search(r'who reports to ([A-Z][a-zA-Z0-9_\-]+(?:\s+[A-Z][a-zA-Z0-9_\-]+)*)', question, re.IGNORECASE)
    if reports_match:
        manager = reports_match.group(1).strip()
        return (
            "MATCH (e:Entity)-[:REPORTS_TO]->(m:Entity {name: \"" + manager + "\"}) "
            "RETURN e.name AS subject, 'REPORTS_TO' AS rel, m.name AS object LIMIT 100"
        )

    # role query for specific titles
    role_match = re.search(r'who is the (.*?) at ([A-Z][a-zA-Z0-9_\-]+(?:\s+[A-Z][a-zA-Z0-9_\-]+)*)', question, re.IGNORECASE)
    if role_match:
        raw_role = role_match.group(1).strip()
        role = raw_role if raw_role.isupper() else raw_role.title()
        company = role_match.group(2).strip()
        return (
            "MATCH (e:Entity)-[:HAS_ROLE]->(r:Role {title: \"" + role + "\"}) "
            "MATCH (e)-[:WORKS_AT]->(c:Company {name: \"" + company + "\"}) "
            "RETURN e.name AS subject, 'HAS_ROLE' AS rel, r.title AS object LIMIT 100"
        )

    # company query: who works at <company>
    work_at_match = re.search(r'who (?:works|work) at ([A-Z][a-zA-Z0-9_\-]+(?:\s+[A-Z][a-zA-Z0-9_\-]+)*)', question, re.IGNORECASE)
    if work_at_match:
        company = work_at_match.group(1).strip()
        return (
            "MATCH (e:Entity)-[:WORKS_AT]->(c:Company {name: \"" + company + "\"}) "
            "RETURN e.name AS subject, 'WORKS_AT' AS rel, c.name AS object LIMIT 100"
        )

    # role-of-entity query
    role_of_match = re.search(r'what (?:is the role|role does .* have|is .* role) of ([A-Z][a-zA-Z0-9_\-]+(?:\s+[A-Z][a-zA-Z0-9_\-]+)*)', question, re.IGNORECASE)
    if role_of_match:
        person = role_of_match.group(1).strip()
        return (
            "MATCH (e:Entity {name: \"" + person + "\"})-[:HAS_ROLE]->(r:Role) "
            "RETURN e.name AS subject, 'HAS_ROLE' AS rel, r.title AS object LIMIT 100"
        )

    # company-of-entity query
    works_for_match = re.search(r'what company does ([A-Z][a-zA-Z0-9_\-]+(?:\s+[A-Z][a-zA-Z0-9_\-]+)*) work for', question, re.IGNORECASE)
    if works_for_match:
        person = works_for_match.group(1).strip()
        return (
            "MATCH (e:Entity {name: \"" + person + "\"})-[:WORKS_AT]->(c:Company) "
            "RETURN e.name AS subject, 'WORKS_AT' AS rel, c.name AS object LIMIT 100"
        )

    # fallback: if there is a single quoted or capitalized entity
    if quoted_terms:
        found = quoted_terms
    if len(found) >= 2:
        a = _normalize_name(found[0])
        b = _normalize_name(found[1])
        return (
            "MATCH (a:Entity {name: \"" + a + "\"})-[r]->(b:Entity {name: \"" + b + "\"}) "
            "RETURN a.name AS subject, type(r) AS rel, b.name AS object, r.type AS relprop LIMIT 50"
        )

    # fallback: search for entities with name tokens
    keywords = [t for t in q.split() if len(t) > 3]
    if keywords:
        term = " ".join(keywords[:4])
        return (
            "MATCH (n:Entity) WHERE toLower(n.name) CONTAINS \"" + term + "\" "
            "OPTIONAL MATCH (n)-[r]->(m:Entity) RETURN n.name AS subject, type(r) AS rel, m.name AS object LIMIT 50"
        )

    return None
