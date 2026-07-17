# bank_service.py
from decimal import Decimal
from typing import List
from repo.bank_repo import BankRepo
from repo.user_repo import UserRepo
from models.bank_model import BankModel, TransactionModel


# Custom exceptions for bank service
class AccountNotFoundException(Exception):
    pass
class AccountCreationFailedException(Exception):
    pass
class InsufficientFundsException(Exception):
    pass
class UnknownTransactionException(Exception):
    pass


class BankService():
    def __init__(self):
        # Initialize the repositories for bank and user
        self.repo = BankRepo()
        self.user_repo = UserRepo()

    # Create a new bank account for a user, ensuring the owner exists first
    # throws a ValueError if the owner_id doesn't exist in the user repository
    # raises a custom error if account creation fails for any reason
    async def create_account(self, owner_id: str, account_type: str) -> BankModel:
        # Validate owner exists
        user = await self.user_repo.getUser(owner_id)
        if not user:
            raise ValueError("Owner ID does not correspond to an existing user.")
            
        new_account = await self.repo.create_account(owner_id, account_type)
        if not new_account:
            raise AccountCreationFailedException("Account creation failed")
        return new_account

    # Get a bank account by its ID, raises a custom exception if not found
    async def get_account(self, account_id: str) -> BankModel:
        account = await self.repo.get_account(account_id)
        if not account:
            raise AccountNotFoundException("Account not found")
        return account
    # Get all bank accounts for a specific owner, returns a list of BankModel instances
    async def get_accounts_by_owner(self, owner_id: str) -> list[BankModel]:
        return await self.repo.get_accounts_by_owner(owner_id)

    # Withdraw a specified amount from a bank account, raising a custom exception
    # if the account is not found or if there are insufficient funds
    async def withdraw(self, account_id: str, amount: Decimal) -> TransactionModel:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        account = await self.get_account(account_id)

        if account.balance < amount:
            raise InsufficientFundsException("Account has insufficient funds.")

        transaction = await self.repo.create_withdrawal(account_id, amount)
        if not transaction:
            raise InsufficientFundsException("Account has insufficient funds.")
            
        return transaction

    # Deposit a specified amount into a bank account, raising a custom exception
    # if the account is not found
    async def deposit(self, account_id: str, amount: Decimal) -> TransactionModel:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
            
        # Ensure account exists first
        await self.get_account(account_id)
        
        transaction = await self.repo.create_deposit(account_id, amount)
        if not transaction:
            # This would only happen if the account disappeared between our check and write
            raise AccountNotFoundException("Account not found")
        return transaction

    # Get all transactions for a specific bank account, raises a custom exception 
    # if the account is not found
    async def get_transactions(self, account_id: str) -> List[TransactionModel]:
        # Ensure account exists first
        await self.get_account(account_id)
            
        transactions = await self.repo.get_transactions(account_id)
        if transactions is None:
            raise UnknownTransactionException("Transactions could not be retrieved.")
        return transactions