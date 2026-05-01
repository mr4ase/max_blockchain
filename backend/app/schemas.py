# backend\app\schemas.py


from pydantic import BaseModel, Field
from backend.wallet.wallet import Wallet


class TransactionCreateSchema(BaseModel):
    recipient_address: str
    amount: int = Field(gt=0)
