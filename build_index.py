import os
from scripts.ingest_via_http import ingest_file


def main():
    data_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "data", "org_passages.csv"))
    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}")
        return
    print("Ingesting passages into Neo4j via HTTP transactional endpoint.")
    print("Set NEO4J_HTTP, NEO4J_DATABASE, NEO4J_USER, and NEO4J_PASSWORD if needed.")
    ingest_file(data_path)


if __name__ == "__main__":
    main()
