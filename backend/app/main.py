from fastapi import FastAPI
from routers import query, schema

app = FastAPI(title="Big Data Query Assistant")
app.include_router(query.router)
app.include_router(schema.router)
