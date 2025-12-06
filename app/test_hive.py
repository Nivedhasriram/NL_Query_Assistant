# app/test_hive.py
from pyhive import hive
import pandas as pd

def test_query():
    conn = hive.Connection(host='127.0.0.1', port=10000, username='root', database='nl2hive_demo')
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, SUM(price * quantity) as revenue FROM sales GROUP BY product_id ORDER BY revenue DESC LIMIT 10")
    cols = [d[0] for d in cursor.description] if cursor.description else []
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=cols)
    print(df)

if __name__ == '__main__':
    test_query()
