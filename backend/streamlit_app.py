import os
import streamlit as st
from kg.neo4j_client import Neo4jClient
from llm.answer import generate_answer
from nl2cypher import translate_question_to_cypher


def get_neo4j_client(uri: str, user: str, password: str, database: str = None) -> Neo4jClient:
    return Neo4jClient(uri=uri, user=user, password=password, database=database)


def main():
    st.set_page_config(page_title="KG-RAG QA - Group 109", layout="wide")
    st.title("Knowledge Graph-Augmented QA System — Group 109")
    st.write("Natural language QA over a Neo4j knowledge graph using a free local generative model.")

    # Get configuration from environment
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE")

    # Sidebar: Group Details & Credentials
    with st.sidebar:
        st.header("📋 Group 109 Info")
        st.markdown("""
        **Domain:** Corporate Organizational Charts  
        **Members:** [Team Members]  
        **IDs:** [Student IDs]  
        **Contributions:** [Percentages]
        """)
        st.markdown("---")
        st.header("⚙️ System Configuration")
        st.info(f"""
        **Neo4j URI:** {uri or 'Not set'}  
        **Database:** {database or 'default'}  
        **Status:** {'✅ Connected' if uri and user and password else '❌ Missing credentials'}
        """)
        st.markdown("---")
        st.markdown("""
        ### How to Use
        1. Navigate to **KG Ingestion** to explore the knowledge graph
        2. Use **Query Translator** to see NL→Cypher conversion
        3. Try **KG-RAG Playground** for interactive QA
        """)

    # Validate connection
    if not uri or not user or password is None:
        st.error(
            "❌ Neo4j connection not configured. Set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD environment variables."
        )
        return

    try:
        neo4j_client = get_neo4j_client(uri, user, password, database)
    except Exception as error:
        st.error(f"❌ Could not connect to Neo4j: {error}")
        return

    # Main Tabs
    tab1, tab2, tab3 = st.tabs(["📊 KG Ingestion", "🔄 Query Translator", "🎯 KG-RAG Playground"])

    with tab1:
        st.subheader("Knowledge Graph & Data Ingestion")
        st.markdown("""
        This tab displays information about the knowledge graph structure and ingested data.
        """)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Dataset Source", "org_passages.csv")
            st.metric("Graph Nodes", "Entity, Company, Role, Department")
        with col2:
            st.metric("Dataset Size", "~1000+ passages")
            st.metric("Relations", "WORKS_AT, HAS_ROLE, REPORTS_TO, IN_DEPARTMENT")
        
        st.markdown("---")
        st.markdown("**Sample Ingestion Format:**")
        st.code("""
John Smith is the CEO at TechCorp.
Alice Garcia works in the Legal department.
Dana Patel reports to Morgan Lee.
        """, language="text")

    with tab2:
        st.subheader("Natural Language to Cypher Translator")
        st.markdown("Enter a natural language question and see the generated Cypher query.")
        
        sample_questions = {
            "Who reports to Morgan Lee?": "Who reports to Morgan Lee?",
            "Who works in the Legal department?": "Who works in the Legal department?",
            "Who is the CEO at GigaMatrix?": "Who is the CEO at GigaMatrix?",
            "What company does Alice Johnson work for?": "What company does Alice Johnson work for?",
        }
        
        question = st.selectbox(
            "Select a sample question or enter your own:",
            options=list(sample_questions.keys()) + ["Custom..."]
        )
        
        if question == "Custom...":
            question = st.text_input("Enter your question:")
        else:
            question = sample_questions[question]
        
        if question:
            cypher = translate_question_to_cypher(neo4j_client, question)
            st.write("**Translated Cypher Query:**")
            if cypher:
                st.code(cypher, language="sql")
            else:
                st.warning("Could not translate question to Cypher.")

    with tab3:
        st.subheader("🎯 KG-RAG Playground – Interactive QA")
        st.markdown("Ask questions about the knowledge graph. The system will retrieve facts and generate answers.")
        
        # Query input section
        question = st.text_area(
            "Question",
            value="Who reports to Morgan Lee?",
            height=80,
            placeholder="Enter a natural language question..."
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            generate_btn = st.button("🔍 Generate Answer", use_container_width=True)
        with col3:
            clear_btn = st.button("🔄 Clear", use_container_width=True)
        
        if clear_btn:
            st.rerun()
        
        if generate_btn and question.strip():
            st.markdown("---")
            
            # Step 1: Translate to Cypher
            with st.expander("📝 Step 1: Query Translation", expanded=True):
                cypher = translate_question_to_cypher(neo4j_client, question)
                if cypher:
                    st.code(cypher, language="sql")
                else:
                    st.error("Could not translate question to Cypher.")
                    neo4j_client.close()
                    return
            
            # Step 2: Retrieve facts
            with st.expander("📊 Step 2: Graph Retrieval Results", expanded=True):
                try:
                    facts = neo4j_client.run_query(cypher)
                    if facts:
                        st.json(facts)
                        st.success(f"✅ Retrieved {len(facts)} fact(s) from the knowledge graph.")
                    else:
                        st.info("ℹ️ No facts found in the knowledge graph for this query.")
                        facts = []
                except Exception as error:
                    st.error(f"❌ Query execution failed: {error}")
                    facts = []
            
            # Step 3: Generate answer
            with st.expander("💡 Step 3: Final Generated Answer", expanded=True):
                try:
                    answer = generate_answer(question, facts)
                    st.markdown(f"**Answer:**")
                    st.write(answer)
                except Exception as error:
                    st.error(f"❌ Answer generation failed: {error}")

    neo4j_client.close()


if __name__ == "__main__":
    main()
