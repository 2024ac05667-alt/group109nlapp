import os
import sys

# Use the HTTP ingestion as a fallback so this script does not import spaCy.
from scripts.ingest_via_http import ingest_file as http_ingest_file


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    data_path = os.path.normpath(os.path.join(here, '..', 'data', 'org_passages.csv'))
    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}")
        sys.exit(1)
    print('Ingesting via HTTP transactional endpoint (ensure Neo4j HTTP is enabled)')
    http_ingest_file(data_path)
