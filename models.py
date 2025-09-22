from pydantic import BaseModel
from enum import Enum
from decimal import Decimal

class UserQuery(BaseModel):
    query: str

class Transaction(BaseModel):
    symbol: str
    block_number: int
    tx_number: int
    from_address: str
    to_address: str
    value_hex: str
    value_decimal: Decimal
    is_failed: bool
    is_block_reward: bool

class ResponseType(str, Enum):
    TXT = "TXT"
    FILE = "FILE"
    MD = "MD"
    HTML = "HTML"

class ChatResponse(BaseModel):
    response: str
    response_type: ResponseType
    response_summary : str

class SqlQueryResponse(BaseModel):
    sql_query: str
    summary : str