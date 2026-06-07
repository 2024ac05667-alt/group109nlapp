import csv
import os
import streamlit as st
from kg.neo4j_client import Neo4jClient
from llm.answer import generate_answer
from nl2cypher import translate_question_to_cypher

# Try importing the richer extractor; if unavailable, provide a lightweight fallback
try:
    from kg.ingest import extract_and_ingest
except Exception:
    def extract_and_ingest(neo4j_client, text: str):
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
            neo4j_client.execute_write(
                "MATCH (a:Entity {name:$s}), (c:Company {name:$c}) MERGE (a)-[:WORKS_AT]->(c)",
                {"s": subj, "c": comp},
            )
        if subj and role:
            neo4j_client.execute_write(
                "MERGE (r:Role {title:$role}) MERGE (a:Entity {name:$s}) MERGE (a)-[:HAS_ROLE]->(r)",
                {"s": subj, "role": role},
            )
        if subj and manager:
            neo4j_client.execute_write(
                "MERGE (m:Entity {name:$m}) MERGE (a:Entity {name:$s}) MERGE (a)-[:REPORTS_TO]->(m)",
                {"s": subj, "m": manager},
            )
        if subj and dept:
            neo4j_client.execute_write(
                "MERGE (d:Department {name:$d}) MERGE (a:Entity {name:$s}) MERGE (a)-[:IN_DEPARTMENT]->(d)",
                {"s": subj, "d": dept},
            )


def get_neo4j_client(uri: str, user: str, password: str) -> Neo4jClient:
    return Neo4jClient(uri=uri, user=user, password=password)


def parse_uploaded_csv(uploaded_file):
    if uploaded_file is None:
        return []
    text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    reader = csv.DictReader(text.splitlines())
    return [row.get("text") or row.get("passage") or "" for row in reader if row]


def main():
    st.set_page_config(page_title="KG QA - Group 109", layout="wide")
    st.title("Knowledge Graph-Augmented QA — Group 109")
    st.write("Use Neo4j and a free generative model to answer corporate org chart questions.")

    with st.sidebar:
        st.header("Neo4j connection")
        uri = st.text_input("NEO4J_URI", value=os.environ.get("NEO4J_URI", "bolt://localhost:7687"))
        user = st.text_input("NEO4J_USER", value=os.environ.get("NEO4J_USER", "neo4j"))
        password = st.text_input("NEO4J_PASSWORD", value=os.environ.get("NEO4J_PASSWORD", "password"), type="password")
        st.markdown("---")
        st.markdown("### How to use")
        st.markdown(
            "1. Upload a CSV with a `text` column to ingest facts into Neo4j.\n"
            "2. Ask a question in the main pane.\n"
            "3. Review the generated Cypher, retrieved facts, and final answer."
        )
        st.info("If you need a public Neo4j instance, set the connection values above.")

    try:
        neo4j_client = get_neo4j_client(uri, user, password)
    except Exception as error:
        st.error(f"Could not connect to Neo4j: {error}")
        return

    tab1, tab2 = st.tabs(["Ingest", "Ask a question"])

    with tab1:
        st.subheader("Ingest passages into the graph")
        data_file = st.file_uploader("Upload CSV file", type=["csv"])
        if data_file is not None:
            texts = parse_uploaded_csv(data_file)
            if st.button("Ingest uploaded passages"):
                count = 0
                for text in texts:
                    if text and text.strip():
                        extract_and_ingest(neo4j_client, text)
                        count += 1
                st.success(f"Ingested {count} passages into Neo4j.")
        st.markdown("---")
        st.write("Example CSV rows should use a `text` field with corporate org chart sentences.")

    with tab2:
        st.subheader("Ask a natural language question")
        question = st.text_area("Question", value="Who is the head of the finance department?")
        if st.button("Generate answer"):
            if not question.strip():
                st.warning("Enter a question first.")
            else:
                cypher = translate_question_to_cypher(neo4j_client, question)
                if not cypher:
                    st.error("Could not translate the question to Cypher.")
                else:
                    st.write("**Translated Cypher**")
                    st.code(cypher)
                    try:
                        facts = neo4j_client.run_query(cypher)
                        st.write("**Retrieved facts**")
                        st.json(facts)
                        answer = generate_answer(question, facts)
                        st.write("**Generated answer**")
                        st.write(answer)
                    except Exception as error:
                        st.error(f"Query execution failed: {error}")

    neo4j_client.close()


if __name__ == "__main__":
    main()
