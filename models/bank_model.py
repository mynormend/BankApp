# bank_model.py
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing_extensions import Literal

from models.user_model import UserModel

class BankModel(BaseModel):
    id: str = Field(alias="_id")
    owner_id: str
    account_type: Literal["savings", "checking"]
    balance: Decimal

    model_config = {
        "populate_by_name": True,
    }

class TransactionModel(BaseModel):
    id: str = Field(alias="_id")
    account_id: str
    amount: Decimal
    type: Literal["withdrawal", "deposit"]
    date_time: datetime

    model_config = {
        "populate_by_name": True,
    }

class UserPortfolio(BaseModel):
    user: UserModel
    accounts: list[BankModel]