import os
from kg.neo4j_client import Neo4jClient

def sample_counts():
    client = Neo4jClient()
    cypher = "MATCH (n:Entity) RETURN count(n) AS cnt LIMIT 1"
    res = client.run_query(cypher)
    print(res)

if __name__ == '__main__':
    sample_counts()
