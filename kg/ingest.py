import re


def _load_spacy():
    try:
        import spacy
    except ImportError as err:
        raise ImportError(
            "spaCy is not installed. Install it manually only if you want richer extraction: "
            "python -m pip install spacy && python -m spacy download en_core_web_sm"
        ) from err
    return spacy.load("en_core_web_sm")


def extract_triples(text: str):
    nlp = _load_spacy()
    doc = nlp(text)
    triples = []
    # Very simple SVO extraction heuristic
    for sent in doc.sents:
        subj = None
        verb = None
        obj = None
        for token in sent:
            if token.dep_.endswith("subj"):
                subj = token.text
            if token.pos_ == "VERB":
                verb = token.lemma_
            if token.dep_.endswith("obj"):
                obj = token.text
        if subj and verb and obj:
            triples.append((subj, verb, obj))

    # fallback: use named entities as subjects/objects
    ents = [e.text for e in doc.ents]
    if not triples and len(ents) >= 2:
        triples.append((ents[0], "related_to", ents[1]))

    return triples


def extract_and_ingest(neo4j_client, text: str):
    triples = extract_triples(text)
    for s, p, o in triples:
        s_clean = re.sub(r"[^\w\s-]", "", s).strip()
        o_clean = re.sub(r"[^\w\s-]", "", o).strip()
        p_clean = re.sub(r"[^\w\s-]", "", p).strip()
        cypher = (
            "MERGE (a:Entity {name: $s})\n"
            "MERGE (b:Entity {name: $o})\n"
            "MERGE (a)-[r:REL {type: $p}]->(b)\n"
            "RETURN a.name AS subject, r.type AS rel, b.name AS object"
        )
        neo4j_client.execute_write(cypher, {"s": s_clean, "o": o_clean, "p": p_clean})
