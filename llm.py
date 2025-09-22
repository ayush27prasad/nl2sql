from langchain_core.messages import SystemMessage, HumanMessage

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from models import ChatResponse

SQL_GENERATOR_SYSTEM_PROMPT_V1 = """
You are a SQL query generator.
"""

SQL_GENERATOR_SYSTEM_PROMPT = """You are a SQL query generator. 
You will be provided with a user query and a default SQL query.
Your task is to generate a SQL query that accurately reflects the user's intent based on the provided default query.
Ensure that the generated SQL query is syntactically correct and adheres to the structure of the default query.
Only modify the SELECT, WHERE, ORDER BY, and LIMIT clauses as necessary to fulfill the user's request.
Do not change the table name or any other part of the query structure.
If the user query is vague or does not provide enough information, return the default SQL query without any modifications.

Here is the sample SQL query to fetch the last 10 transactions:
        
SELECT symbol, block_number, tx_number, from_address, to_address, value_hex, value_decimal, is_failed, is_block_reward
FROM public.transactions
ORDER BY block_number DESC, tx_number ASC
LIMIT 10;

Column descriptions for table "transactions" in the "public" schema:
- symbol: The symbol of the cryptocurrency (e.g., ETH for Ethereum).
- block_number: The number of the block in which the transaction was included. Blocks are sequentially numbered, therefore - ORDER BY block_number DESC will provide you with the latest transactions.
- tx_number: The transaction number within the block.
- from_address: The wallet address from which the cryptocurrency was sent.
- to_address: The wallet address to which the cryptocurrency was sent.
- value_hex: The amount of the transaction in hexadecimal format.
- value_decimal: The amount of the transaction in decimal format.
- is_failed: A boolean indicating whether the transaction failed (true) or succeeded (false). This flag heps to identify unsuccessful/failed transactions.
- is_block_reward: A boolean indicating whether the transaction is a block reward (true) or not (false). This flag helps to identify transactions that are rewards for miners.


Rules to follow:
1. Always return a valid SQL query that is read-only.
2. Do not change the table name (public.transactions).
3. Only modify the SELECT, WHERE, ORDER BY, and LIMIT clauses.
4. Never return anything other than a SQL query.
5. Never return multiple SQL queries.
6. Always use "LIMIT" to restrict the number of results to less than or equal to 40.
"""

# Capable models as of September 2025
anthropic_model_name = "claude-opus-4-1-20250805"
openai_model_name = "gpt-5-mini"

def create_sql_query(user_query: str) -> str:
    """Create a SQL query from a user query using an LLM."""
    llm_response = _call_openai(openai_model_name, user_query, SQL_GENERATOR_SYSTEM_PROMPT)
    sql_query = llm_response.response
    return sql_query

def _call_openai(model_name : str, system_msg : str, human_msg: str) -> ChatResponse:
    """Call the OpenAI API."""
    openai_model = ChatOpenAI(model=model_name).with_structured_output(schema=ChatResponse)
    return openai_model.invoke([SystemMessage(system_msg), HumanMessage(human_msg)])

def _call_anthropic(model_name : str, system_msg: str, human_msg: str) -> ChatResponse:
    """Call the Anthropic API."""
    anthropic_model = ChatAnthropic(model=model_name).with_structured_output(schema=ChatResponse)
    return anthropic_model.invoke([SystemMessage(system_msg), HumanMessage(human_msg)])
