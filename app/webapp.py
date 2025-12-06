# app/webapp.py
from flask import Flask, request, render_template_string
from app.main import run_pipeline, DEFAULT_SCHEMA

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>NL → Hive Query Assistant</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-4">
  <h1 class="mb-3">Natural Language Hive Query Assistant</h1>
  <p class="text-muted">Type a question about the sales data. The system will generate Hive SQL using Gemini (and a secondary LLM) and run it on Hive.</p>

  <form method="POST" class="card card-body mb-3">
    <div class="mb-3">
      <label for="question" class="form-label">Question</label>
      <textarea class="form-control" id="question" name="question" rows="3" placeholder="Example: Show top 5 products by total revenue last month">{{ question or "" }}</textarea>
    </div>
    <button type="submit" class="btn btn-primary">Run Query</button>
  </form>

  {% if error %}
    <div class="alert alert-danger">{{ error }}</div>
  {% endif %}

  {% if best_sql %}
    <div class="card mb-3">
      <div class="card-header">Chosen SQL</div>
      <div class="card-body">
        <pre class="mb-0"><code>{{ best_sql }}</code></pre>
      </div>
    </div>
  {% endif %}

  {% if result_html %}
    <div class="card">
      <div class="card-header">Result</div>
      <div class="card-body">
        {{ result_html|safe }}
      </div>
    </div>
  {% endif %}
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    best_sql = ""
    result_html = ""
    error = ""

    if request.method == "POST":
        question = (request.form.get("question") or "").strip()
        if question:
            try:
                out = run_pipeline(question, DEFAULT_SCHEMA)
                best_sql = out.get("best_sql", "")
                df = out.get("df")
                if df is not None:
                    result_html = df.to_html(index=False, classes="table table-striped table-sm")
                else:
                    result_html = "<p>No rows returned.</p>"
            except Exception as e:
                error = str(e)

    return render_template_string(PAGE,
                                  question=question,
                                  best_sql=best_sql,
                                  result_html=result_html,
                                  error=error)

if __name__ == "__main__":
    app.run(debug=True)
