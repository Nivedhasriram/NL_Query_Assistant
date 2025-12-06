# app/main.py
import os
import re
import argparse
import time
from typing import List, Tuple, Dict, Any

from dotenv import load_dotenv
load_dotenv()

from app.llm_wrappers import GeminiWrapper, HFDeepSeekWrapper
from app.hive_client import HiveClient
from app.comparator import rank_candidates

DEFAULT_SCHEMA = "TABLE nl2hive_demo.sales(product_id string, price double, quantity int, sale_date string);"
HIVE_HOST = os.getenv("HIVE_HOST", "127.0.0.1")
HIVE_PORT = int(os.getenv("HIVE_PORT", "10000"))
USE_STUB = os.getenv("USE_STUB", "0") == "1"

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
HF_MODEL = os.getenv("HF_MODEL", "google/flan-t5-large")

SQL_START_RE = re.compile(r"(SELECT|WITH|CREATE|INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER)[\s\S]*", re.IGNORECASE)

def extract_sql(text: str) -> str:
    if not text:
        return ""
    m = SQL_START_RE.search(text)
    return (m.group(0) if m else text).strip()

def clean_sql(s: str) -> str:
    if not s:
        return s
    s = s.strip()
    s = s.replace("```sql", "").replace("```SQL", "")
    s = s.replace("```", "")
    s = s.replace("`", "")
    return s.strip()

def ensure_select_limit(sql: str, default_limit: int = 100) -> str:
    if not sql:
        return sql
    s = sql.strip()
    while s.endswith(";"):
        s = s[:-1].rstrip()
    if s.upper().startswith("SELECT") and "LIMIT" not in s.upper():
        s = s + f" LIMIT {default_limit}"
    return s

def build_prompt(nl: str, schema_text: str) -> str:
    try:
        from app.prompts import nl_to_hive_prompt
        return nl_to_hive_prompt(nl, schema_text)
    except Exception:
        return f"Schema:\n{schema_text}\n\nConvert this natural language request to a Hive SQL query:\n{nl}\nSQL:"

def instantiate_translators():
    translators = []

    # ---- Gemini (primary) ----
    try:
        translators.append((
            "gemini",
            GeminiWrapper(
                model=GEMINI_MODEL,
                api_key=os.getenv("GOOGLE_GENAI_API_KEY")
            )
        ))
    except Exception as e:
        print("[warn] GeminiWrapper not available:", e)

    # ---- Hugging Face DeepSeek (secondary) ----
    try:
        translators.append((
            "deepseek",
            HFDeepSeekWrapper()
        ))
    except Exception as e:
        print("[warn] HFDeepSeekWrapper not available:", e)

    return translators


def run_pipeline(nl: str, schema_text: str = DEFAULT_SCHEMA) -> Dict[str, Any]:
    print("[info] Starting NL->Hive pipeline")
    prompt = build_prompt(nl, schema_text)
    hive = HiveClient(host=HIVE_HOST, port=HIVE_PORT)
    candidates: List[str] = []

    if USE_STUB:
        print("[info] Using STUB mode for candidate SQLs (no LLM calls)")
        candidates = [
            "SELECT product_id, SUM(price * quantity) AS revenue FROM nl2hive_demo.sales GROUP BY product_id ORDER BY revenue DESC LIMIT 10;",
            "SELECT product_id, SUM(price*quantity) AS revenue FROM nl2hive_demo.sales GROUP BY product_id ORDER BY revenue DESC LIMIT 5;",
            "SELECT product_id, SUM(price*quantity) AS revenue FROM sales GROUP BY product_id ORDER BY revenue DESC;"
        ]
    else:
        translators = instantiate_translators()
        if not translators:
            raise RuntimeError("No translators available (Gemini/HF not configured)")

        for name, t in translators:
            try:
                print(f"[info] Asking translator: {name}")
                out = t.generate(prompt, max_tokens=512)
                sql_candidate = clean_sql(extract_sql(out))
                print(f"[{name}] candidate:\n{sql_candidate}\n---")
                if sql_candidate and not sql_candidate.startswith("--ERROR--"):
                    candidates.append(sql_candidate)
                else:
                    print(f"[warn] {name} returned error: {out[:120]}")
            except Exception as e:
                print(f"[warn] generation failed for {name}:", e)

    # Clean/filter candidates
    candidates = [clean_sql(c) for c in candidates if c and not c.startswith("--ERROR--")]
    if not candidates:
        raise RuntimeError("No valid SQL candidates produced")

    print("[info] Ranking candidate queries...")
    scored = rank_candidates(candidates, hive_client=hive)
    if not scored:
        raise RuntimeError("Ranking produced no valid candidates")

    for sql, score in scored:
        print(f"score={score} sql={sql}")

    best_sql, best_score = scored[0]
    best_sql = ensure_select_limit(best_sql, default_limit=100)

    exec_sql_clean = best_sql.strip()
    while exec_sql_clean.endswith(";"):
        exec_sql_clean = exec_sql_clean[:-1].rstrip()

    explain_text = ""
    try:
        explain_text = hive.explain(exec_sql_clean)
        print("[info] EXPLAIN snippet:\n", explain_text[:500])
    except Exception as e:
        print("[warn] EXPLAIN failed:", e)

    df = None
    try:
        df = hive.execute(exec_sql_clean, fetch=True)
        if df is not None:
            print("[info] Query result:\n", df.head(20))
    except Exception as e:
        print("[error] Execution failed:", e)

    return {
        "best_sql": exec_sql_clean,
        "score": best_score,
        "explain": explain_text,
        "df": df,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nl", required=True, help="Natural language query")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    t0 = time.time()
    out = run_pipeline(args.nl, args.schema)
    print("\n[info] Best SQL:\n", out["best_sql"])
    if out["df"] is not None:
        print("\n[info] Result head:\n", out["df"].head(20))
    print(f"[info] Done. Elapsed {time.time()-t0:.2f}s")

if __name__ == "__main__":
    main()
