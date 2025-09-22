import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from db import Database
from llm import create_sql_query, create_md_response
from models import UserQuery
from utils import is_valid_sql_query
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONNECTION_STRING = os.getenv("DB_URL")
db = Database(dsn=DATABASE_CONNECTION_STRING)

# App with DB lifespan
app = FastAPI(lifespan=db.lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for specific frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/api/v1/transactions/chat")
async def get_transactions(payload: UserQuery) -> str:
    response = await resolve_user_query(payload.query)
    return response

async def resolve_user_query(user_query: str) -> str:

    # Create SQL query from user query using LLM
    sql_llm_response = create_sql_query(user_query)
    sql_query = sql_llm_response.response
    sql_summary = sql_llm_response.response_summary
    print("Generated SQL Query:", sql_query)

    # Validate the generated SQL query
    if not is_valid_sql_query(sql_query):
        raise ValueError("Generated SQL query is not valid or safe.")

    # Fetch data from the database using the generated SQL query
    rows = await db.fetch_all(sql_query)
    query_results = [dict(row) for row in rows]

    # Return formatted markdown response using LLM
    return create_md_response(data=query_results, sql_query_used=sql_query, sql_query_summary=sql_summary, user_query=user_query)


