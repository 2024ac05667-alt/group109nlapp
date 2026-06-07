import os
import traceback

try:
    from neo4j import GraphDatabase
except Exception:
    GraphDatabase = None


class Neo4jClient:
    """Neo4j client with graceful fallback when the database is unavailable.

    If the bolt driver cannot be created, methods become no-ops and return
    empty results so the application can run in environments without Neo4j.
    """

    def __init__(self, uri: str = None, user: str = None, password: str = None):
        uri = uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = user or os.environ.get("NEO4J_USER", "neo4j")
        password = password or os.environ.get("NEO4J_PASSWORD", "password")
        self._available = False
        self.driver = None
        if GraphDatabase is None:
            print("Neo4j driver not installed; running in fallback mode (no DB).")
            return

        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # test a quick connection
            with self.driver.session() as s:
                s.run("RETURN 1")
            self._available = True
        except Exception:
            print("Warning: Could not connect to Neo4j at", uri)
            traceback.print_exc()
            self.driver = None
            self._available = False

    def close(self):
        if self.driver:
            try:
                self.driver.close()
            except Exception:
                pass

    def run_query(self, cypher: str, parameters: dict = None):
        if not self._available or self.driver is None:
            print("Neo4j not available — run_query returning empty list.")
            return []
        with self.driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]

    def execute_write(self, cypher: str, parameters: dict = None):
        if not self._available or self.driver is None:
            print("Neo4j not available — execute_write is a no-op.")
            return
        with self.driver.session() as session:
            session.run(cypher, parameters or {})
