# bank_controller.py
from pydantic import BaseModel, BeforeValidator, Field
from typing_extensions import Annotated, Literal
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, HTTPException
from service.bank_service import (
    BankService, 
    AccountNotFoundException, 
    AccountCreationFailedException,
    InsufficientFundsException, 
    UnknownTransactionException
)


bank_service = BankService()
router = APIRouter()

PyObjectId = Annotated[str, BeforeValidator(str)]

# Data models used for servers response to client
class BankResponse(BaseModel):
    bank_id: PyObjectId = Field(alias="_id")
    owner_id: str
    account_type: Literal["savings", "checking"]
    balance: Decimal
    
    model_config = {
        "populate_by_name": True,
    }

class TransactionResponse(BaseModel):
    transaction_id: PyObjectId = Field(alias="_id")
    date_time: datetime
    amount: Decimal
    type: str
    
    model_config = {
        "populate_by_name": True,
    }

# API endpoint to create a new bank account, returns the created BankResponse model
@router.post("/account", response_model=BankResponse, status_code=201)
async def create_account(owner_id: str, account_type: Literal["savings", "checking"]):
    try:
        account_model = await bank_service.create_account(owner_id, account_type)
        return account_model.model_dump(by_alias=True)
    except (ValueError, AccountCreationFailedException) as e:
        raise HTTPException(status_code=400, detail=str(e))

# API endpoint to fetch all bank accounts for a specific owner, returns a list of BankResponse models
@router.get("/account", response_model=list[BankResponse])
async def get_accounts_by_owner(owner_id: str):
    accounts = await bank_service.get_accounts_by_owner(owner_id)
    return [acc.model_dump(by_alias=True) for acc in accounts]

# API endpoint to fetch a specific bank account by its ID, returns a BankResponse model
@router.get("/account/{account_id}", response_model=BankResponse)
async def get_account(account_id: str):
    try:
        account_model = await bank_service.get_account(account_id)
        return account_model.model_dump(by_alias=True)
    except AccountNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

# API endpoint to withdraw from a bank account, returns the created TransactionResponse model
@router.post("/account/{account_id}/withdraw", response_model=TransactionResponse, status_code=201)
async def withdraw(account_id: str, amount: Decimal):
    try:
        transaction_model = await bank_service.withdraw(account_id, amount)
        # FIX: Dump transaction model to dict preserving "_id"
        return transaction_model.model_dump(by_alias=True)
    except AccountNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (InsufficientFundsException, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

# API endpoint to deposit into a bank account, returns the created TransactionResponse model
@router.post("/account/{account_id}/deposit", response_model=TransactionResponse, status_code=201)
async def deposit(account_id: str, amount: Decimal):
    try:
        transaction_model = await bank_service.deposit(account_id, amount)
        # FIX: Dump transaction model to dict preserving "_id"
        return transaction_model.model_dump(by_alias=True)
    except AccountNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# API endpoint to fetch all transactions for a specific bank account, returns a list of TransactionResponse models
@router.get("/account/{account_id}/transactions", response_model=list[TransactionResponse])
async def get_transactions(account_id: str):
    try:
        transactions = await bank_service.get_transactions(account_id)
        return [tx.model_dump(by_alias=True) for tx in transactions]
    except AccountNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnknownTransactionException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))