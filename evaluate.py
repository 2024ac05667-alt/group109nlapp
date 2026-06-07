from kg.neo4j_client import Neo4jClient
from nl2cypher import translate_question_to_cypher

SAMPLE_QUESTIONS = [
    "Who is the Chief Financial Officer at Apex Systems?",
    "Who reports to the head of Engineering?",
    "Which employee works in the Marketing department?",
    "What is the role of Alex Smith?",
]


def main():
    client = Neo4jClient()
    print("Running sample evaluation questions on the current Neo4j graph.")
    for question in SAMPLE_QUESTIONS:
        print(f"\nQuestion: {question}")
        cypher = translate_question_to_cypher(client, question)
        print(f"Translated Cypher: {cypher}")
        if cypher:
            records = client.run_query(cypher)
            print("Results:")
            for record in records:
                print(record)
        else:
            print("No Cypher translation available for this question.")
    client.close()


if __name__ == "__main__":
    main()
