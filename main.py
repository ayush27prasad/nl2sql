import os
from typing import List
from fastapi import FastAPI, Query
from db import Database
from llm import create_sql_query
from models import Transaction, UserQuery
from utils import is_valid_sql_query
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONNECTION_STRING = os.getenv("DB_URL")
db = Database(dsn=DATABASE_CONNECTION_STRING)

# App with DB lifespan
app = FastAPI(lifespan=db.lifespan)


@app.post("/transactions", response_model=List[Transaction])
async def get_transactions(payload: UserQuery):
    response = await fetch_transactions_data(payload.query)
    return response

async def fetch_transactions_data(user_query: str) -> List[Transaction]:

    sql_query = create_sql_query(user_query)

    print("Generated SQL Query:", sql_query)  # Debugging line

    if not is_valid_sql_query(sql_query):
        raise ValueError("Generated SQL query is not valid or safe.")

    rows = await db.fetch_all(sql_query)
    return [Transaction(**dict(row)) for row in rows]
