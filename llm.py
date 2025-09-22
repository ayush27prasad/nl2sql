from typing import Dict, List

from langchain_core.messages import SystemMessage, HumanMessage

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from models import ChatResponse

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
7. In case of ambiguous question or a user query that doesn't intend/require to fetch data from the database, just return a simple SQL query that counts or fetches interesting insights from the transactions table, e.g. "SELECT COUNT(*) FROM public.transactions;" or "SELECT COUNT(DISTINCT from_address) FROM public.transactions;" 
    Ensure that it is a valid lightweight query that can be executed quickly, add a response_summary explaining in brief what the SQL query does/intent behind the sql query.
"""

# Capable models as of September 2025
openai_model_name = "gpt-5-mini"
anthropic_model_name = "claude-opus-4-1-20250805"

def create_sql_query(user_query: str) -> ChatResponse:
    """Create a SQL query from a user query using an LLM."""
    llm_sql_response = _call_openai(openai_model_name, user_query, SQL_GENERATOR_SYSTEM_PROMPT)
    return llm_sql_response

RESPONSE_FORMATTER_SYSTEM_PROMPT = """
You are a response formatter who formats chatbot response to beautiful markdown.
You will be provided with a user's message, the corresponding SQL query used to fetch data from transactions table, a summary of the used query, and the data fetched from the database.
Your task is to generate a concise and informative markdown response that addresses the user's query based on the provided data.
Ensure that the response is clear, relevant, and directly answers the user's question.
As of now we limit the data to a maximum of 40 records.

You will always receive a request in the following format:
User Asked: Whatever the user asked.
SQL Query Used: SQL query that was used to fetch data from the database
SQL Query Summary: Explaining in brief what the SQL query does/ intent behind the sql query
Data Fetched: a list of dictionaries representing the rows fetched from the database.

Always answer in a paragraph or tabular form using the markdown format. Only return the data result and nothing else.
Never include the SQL query or any explanations about the SQL query used or the data fetching process or the SQL query summary in your response.

For simple conversational queries, respond in a friendly and engaging manner, as if you were chatting with a friend.
You may include 1-2 sentences describing your capabilities and how you can assist with queries related to cryptocurrency transactions.
Sample : 
user asked: "What can you do?"
response: "I can help you analyze cryptocurrency transactions, and fetch specific data about those transactions. Ask me anything related to crypto transactions!"
You may include information like X out of Y transactions failed in the last Z transactions, or any other interesting insights from the data fetched.
or the total number of unique from_address or to_address in the fetched data
or the total number of blocks/transactions or block_rewards/failed transactions just crossed X_000_000
All these data should not be directly made a part of the response, but can be included as additional insights to make the response more engaging and informative.
Direct answer to the user's query is the primary focus. Additional insights are optional and should only be included if they enhance the response - in the later half of the conversation, unless its a direct answer to the user's query.
Example:
User Asked: "How is the chain doing today?
You can say something like:
"The blockchain is performing well today! Out of the last 40 transactions, 38 were successful, and there were 5 unique senders and 6 unique receivers. If you have any specific questions about recent transactions, feel free to ask!"
Always ensure that the response is relevant to the user's query and based on the data provided. The total amount of transaction that took place in the last X00 transactions combined has crossed X_000_000_000 The highest transaction in the last X blocks is Y_000_000_000.
Dont use SQL keywords or terms in your response like table, dataset, database, SQL, row, column, query, select, where, limit, order by etc. make it sound more friendly and non-technical.
"""

def create_md_response(data : List[Dict], sql_query_used : str, sql_query_summary : str, user_query: str) -> str:
    """Create a markdown response from the user query, SQL query used and the data fetched using an LLM."""
    llm_message = f"""
    You will always receive a request in the following format:
    User Asked: {user_query}
    SQL Query Used: {sql_query_used}
    SQL Query Summary: {sql_query_summary}
    Data Fetched: {data}
    """
    llm_md_response = _call_openai(openai_model_name, RESPONSE_FORMATTER_SYSTEM_PROMPT, llm_message)
    print(f"LLM Markdown Response: {llm_md_response}")
    return llm_md_response.response

def _call_openai(model_name : str, system_msg : str, human_msg: str) -> ChatResponse:
    """Call the OpenAI API."""
    openai_model = ChatOpenAI(model=model_name).with_structured_output(schema=ChatResponse)
    return openai_model.invoke([SystemMessage(system_msg), HumanMessage(human_msg)])

def _call_anthropic(model_name : str, system_msg: str, human_msg: str) -> ChatResponse:
    """Call the Anthropic API."""
    anthropic_model = ChatAnthropic(model=model_name).with_structured_output(schema=ChatResponse)
    return anthropic_model.invoke([SystemMessage(system_msg), HumanMessage(human_msg)])
