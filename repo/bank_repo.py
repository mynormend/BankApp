# bank_repo.py
from pymongo import AsyncMongoClient
from typing import Optional
from decimal import Decimal
import os
from dotenv import load_dotenv
from models.bank_model import BankModel, TransactionModel 
from datetime import datetime
from bson import Decimal128, ObjectId

load_dotenv()
uri = os.getenv("MONGO_URL")
db_name = os.getenv("MONGODB_DB")

class BankRepo():
    # MongoDB connection and collection initialization
    def __init__(self):
        self.client = AsyncMongoClient(uri)
        self.db = self.client[db_name]
        self.accounts_collection = self.db["accounts"]
        self.transactions_collection = self.db["transactions"]

    # Create a new bank account in the database, initializing the balance to 0.00
    async def create_account(self, owner_id: str, account_type: str) -> Optional[BankModel]:
        new_account = {
            "owner_id": owner_id,
            "account_type": account_type,
            "balance": Decimal128(Decimal("0.00")) # Precision-safe initialization
        }
        result = await self.accounts_collection.insert_one(new_account)
        new_account["_id"] = str(result.inserted_id)
        new_account["balance"] = new_account["balance"].to_decimal()
        
        return BankModel(**new_account)

    # Fetch a bank account by its ID, returning a BankModel instance or None if not found
    async def get_account(self, account_id: str) -> Optional[BankModel]:
        try:
            account = await self.accounts_collection.find_one({"_id": ObjectId(account_id)})
        except Exception:
            return None # Handle malformed ObjectId strings gracefully
            
        if account:
            account["_id"] = str(account["_id"])
            if isinstance(account["balance"], Decimal128):
                account["balance"] = account["balance"].to_decimal()
            return BankModel(**account)
        return None
    
    # Fetch all bank accounts for a given owner, returning a list of BankModel instances
    async def get_accounts_by_owner(self, owner_id: str) -> list[BankModel]:
        cursor = self.accounts_collection.find({"owner_id": owner_id})
        accounts_raw = await cursor.to_list(length=100)
        
        formatted_accounts = []
        for acc in accounts_raw:
            acc["_id"] = str(acc["_id"])
            if isinstance(acc["balance"], Decimal128):
                acc["balance"] = acc["balance"].to_decimal()
            formatted_accounts.append(BankModel(**acc))
            
        return formatted_accounts

    # Create a withdrawal transaction, ensuring decimal precision and overdraft protection
    # if it bypasses the service level check.
    async def create_withdrawal(self, account_id: str, amount: Decimal) -> Optional[TransactionModel]:
        # Keep the exact same atomic logic: protect against the concurrency overdraft race condition
        result = await self.accounts_collection.update_one(
            {
                "_id": ObjectId(account_id),
                "balance": {"$gte": Decimal128(amount)}
            },
            {"$inc": {"balance": Decimal128(-amount)}}
        )

        if result.modified_count == 0:
            return None

        transaction = {
            "account_id": account_id,
            "amount": Decimal128(amount),
            "type": "withdrawal",
            "date_time": datetime.utcnow()
        }
        # Insert the transaction into the transactions collection and return a TransactionModel instance
        tx_result = await self.transactions_collection.insert_one(transaction)
        transaction["_id"] = str(tx_result.inserted_id)
        transaction["amount"] = amount
        
        return TransactionModel(**transaction)

    # Create a deposit transaction, ensuring decimal precision and returning a TransactionModel instance
    async def create_deposit(self, account_id: str, amount: Decimal) -> Optional[TransactionModel]:
        result = await self.accounts_collection.update_one(
            {"_id": ObjectId(account_id)},
            {"$inc": {"balance": Decimal128(amount)}}
        )
        if result.matched_count == 0:
            return None

        transaction = {
            "account_id": account_id,
            "amount": Decimal128(amount),
            "type": "deposit",
            "date_time": datetime.utcnow()
        }
        # Insert the transaction into the transactions collection and return a TransactionModel instance
        tx_result = await self.transactions_collection.insert_one(transaction)
        transaction["_id"] = str(tx_result.inserted_id)
        transaction["amount"] = amount
        
        return TransactionModel(**transaction)

    # Fetch all transactions for a specific bank account, returning a list of TransactionModel instances
    async def get_transactions(self, account_id: str) -> list[TransactionModel]:
        cursor = self.transactions_collection.find({"account_id": account_id})
        transactions_raw = await cursor.to_list(length=100)
        
        formatted_transactions = []
        for tx in transactions_raw:
            tx["_id"] = str(tx["_id"])
            if isinstance(tx["amount"], Decimal128):
                tx["amount"] = tx["amount"].to_decimal()
            formatted_transactions.append(TransactionModel(**tx))
            
        return formatted_transactions