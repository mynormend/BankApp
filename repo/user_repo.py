# user_repo.py
import os
from pymongo import AsyncMongoClient
from typing import Optional
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
from models.user_model import UserModel  # <-- Import the new model

load_dotenv()
uri = os.getenv("MONGO_URL")
db_name = os.getenv("MONGODB_DB")

class UserRepo():
    # MongoDB connection and collection initialization
    def __init__(self):
        self.client = AsyncMongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["users"]

    # Fetch all users from the database, returning a list of UserModel instances
    async def getAllUsers(self) -> list[UserModel]:    
        cursor = self.collection.find({})
        users_raw = await cursor.to_list(length=100)
        return [UserModel(**user) for user in users_raw]
    
    # Fetch a single user by username, returning a UserModel instance or None if not found
    async def getUser(self, username) -> Optional[UserModel]:
        user_dict = await self.collection.find_one({"_id": username})
        if user_dict:
            return UserModel(**user_dict)  # <-- Return the Model
        return None
    
    # Add a new user to the database, returning a UserModel instance or None if the username already exists 
    async def addUser(self, username, fname, lname, email, passwd, role="user") -> Optional[UserModel]:
        new_user_dict = {
            "_id": username,  
            "fname": fname,
            "lname": lname,
            "email": email,
            "password": passwd,
            "role": role
        }
        try:
            await self.collection.insert_one(new_user_dict)
            return UserModel(**new_user_dict)
        except DuplicateKeyError:
            return None
        
    # Delete a user by username, returning a UserModel instance or None if not found
    async def delUser(self, username) -> Optional[UserModel]:
        deleted_user_dict = await self.collection.find_one_and_delete({"_id": username})
        if deleted_user_dict:
            return UserModel(**deleted_user_dict)
        return None