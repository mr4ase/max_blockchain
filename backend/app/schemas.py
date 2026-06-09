# backend\app\schemas.py

from pydantic import BaseModel, Field


class TransactionCreateSchema(BaseModel):
    recipient_address: str
    amount: int = Field(gt=0)
