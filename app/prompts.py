# app/prompts.py
def nl_to_hive_prompt(nl: str, schema_text: str) -> str:
    return f"""
You are an expert translator that converts natural language questions into HiveQL (Apache Hive SQL).
Do not add explanation — just output the final Hive query only.

Schema:
{schema_text}

Examples:
# Example 1
NL: "How many users signed up in January 2024?"
SQL: SELECT COUNT(*) FROM users WHERE signup_date >= '2024-01-01' AND signup_date < '2024-02-01';

# Example 2
NL: "Top 5 products by revenue last month"
SQL: SELECT product_id, SUM(price * quantity) as revenue FROM sales WHERE sale_date >= date_sub(current_date, 30) GROUP BY product_id ORDER BY revenue DESC LIMIT 5;

Now convert to HiveQL.

Natural language: \"{nl}\"
SQL:
"""
