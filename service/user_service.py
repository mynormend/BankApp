# user_service.py
from repo.user_repo import UserRepo
from models.user_model import UserModel
from typing import Optional
from repo.bank_repo import BankRepo

class UserAlreadyExistsException(Exception):
    pass

class UserNotFoundException(Exception):
    pass

class UserService():
    def __init__(self):
        self.repo = UserRepo()
        self.bank_repo = BankRepo() # <-- FIX: Initialize bank_repo here!

    async def getAllUsers(self) -> list[UserModel]:
        return await self.repo.getAllUsers()
    
    async def getUser(self, username) -> Optional[UserModel]:
        user = await self.repo.getUser(username)
        if not user:
            raise UserNotFoundException("User not found")
        return user
    
    async def addUser(self, username, fname, lname, email, passwd, role="user") -> UserModel:
        created_user = await self.repo.addUser(username, fname, lname, email, passwd, role) 
        if not created_user:
            raise UserAlreadyExistsException("User already exists")
        return created_user
    
    async def delUser(self, username) -> UserModel:
        deleted_user = await self.repo.delUser(username)
        if not deleted_user:
            raise UserNotFoundException("User not found") 
        
        # Cascading delete of accounts and transactions
        cursor = self.bank_repo.accounts_collection.find({"owner_id": username})
        accounts = await cursor.to_list(length=100)
        
        for account in accounts:
            account_id = str(account["_id"])
            await self.bank_repo.transactions_collection.delete_many({"account_id": account_id})
            await self.bank_repo.accounts_collection.delete_one({"_id": account["_id"]})

        return deleted_user