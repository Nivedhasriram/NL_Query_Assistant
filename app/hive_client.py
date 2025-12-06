# app/hive_client.py
from pyhive import hive
from TCLIService.ttypes import TOperationState
import pandas as pd

class HiveClient:
    def __init__(self, host="localhost", port=10000, username=None, database="default"):
        self.conn = hive.Connection(host=host, port=port, username=username, database=database)
    
    def execute(self, query: str, fetch: bool=True, limit: int=None):
        cursor = self.conn.cursor()
        q = query
        if limit:
            q = f"SELECT * FROM ({query}) t LIMIT {limit}"
        cursor.execute(q)
        if fetch:
            cols = [d[0] for d in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return pd.DataFrame(rows, columns=cols)
        return None

    def explain(self, query: str):
        cursor = self.conn.cursor()
        cursor.execute(f"EXPLAIN {query}")
        rows = cursor.fetchall()
        return "\n".join([r[0] for r in rows])
