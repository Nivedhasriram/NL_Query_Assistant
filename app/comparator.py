# app/comparator.py
import sqlparse
import re

FORBIDDEN = ["DROP", "TRUNCATE", "ALTER", "DELETE", "INSERT OVERWRITE"]

def syntax_ok(sql: str) -> bool:
    try:
        parsed = sqlparse.parse(sql)
        return len(parsed) > 0
    except Exception:
        return False

def contains_forbidden(sql: str) -> bool:
    s = sql.upper()
    return any(tok in s for tok in FORBIDDEN)

def rank_candidates(candidates: list, hive_client, dryrun_limit=1):
    scored = []
    for sql in candidates:
        score = 0
        s_ok = syntax_ok(sql)
        if s_ok:
            score += 1
        if not contains_forbidden(sql):
            score += 1
        # dry-run: try explain
        try:
            _ = hive_client.explain(sql)
            score += 2
            # attempt a sample execute with limit
            try:
                df = hive_client.execute(sql, fetch=True, limit=dryrun_limit)
                if df is not None:
                    score += (1 if len(df) >= 0 else 0)
            except Exception:
                score -= 1
        except Exception:
            score -= 1
        scored.append((sql, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
