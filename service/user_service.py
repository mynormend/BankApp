# user_service.py
import bcrypt

from repo.user_repo import UserRepo
from models.user_model import UserModel
from typing import Optional
from repo.bank_repo import BankRepo


# Exceptions needed for user service
class UserAlreadyExistsException(Exception):
    pass

class UserNotFoundException(Exception):
    pass

class UserService():
    def __init__(self):
        # Initialize the repositories for user and bank operations, doesn't add anything yet
        self.repo = UserRepo()
        self.bank_repo = BankRepo()

    # Fetch all users from the repository and return them as a list of UserModel instances
    async def getAllUsers(self) -> list[UserModel]:
        return await self.repo.getAllUsers()

    # Fetch a single user by username, raises the custom exception if not found
    async def getUser(self, username) -> Optional[UserModel]:
        user = await self.repo.getUser(username)
        if not user:
            raise UserNotFoundException("User not found")
        return user
    
    # Add a new user to the repository, raises the custom exception if the user already exists
    async def addUser(self, username, fname, lname, email, passwd, role="user") -> UserModel:
        password_bytes = passwd.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
        secure_password_string = hashed_password_bytes.decode('utf-8')
        created_user = await self.repo.addUser(username, fname, lname, email, secure_password_string, role)
        if not created_user:
            raise UserAlreadyExistsException("User already exists")
        return created_user
    
    # Delete a user by username, raises the custom exception if the user is not found. 
    # Also deletes bank accounts and transactions.
    async def delUser(self, username) -> UserModel:
        deleted_user = await self.repo.delUser(username)
        if not deleted_user:
            raise UserNotFoundException("User not found") 
        
        # This is where the the bank accounts are fetched
        cursor = self.bank_repo.accounts_collection.find({"owner_id": username})
        accounts = await cursor.to_list(length=100)
        
        # to then delete all accounts and their transactions
        for account in accounts:
            account_id = str(account["_id"])
            await self.bank_repo.transactions_collection.delete_many({"account_id": account_id})
            await self.bank_repo.accounts_collection.delete_one({"_id": account["_id"]})

        return deleted_user