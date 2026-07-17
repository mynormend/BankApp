# user_repo.py
from pymongo import AsyncMongoClient
from typing import Optional
from pymongo.errors import DuplicateKeyError
import os
from dotenv import load_dotenv
from models.user_model import UserModel  # <-- Import the new model

load_dotenv()
uri = os.getenv("MONGO_URL")
db_name = os.getenv("MONGODB_DB")

class UserRepo():
    def __init__(self):
        self.client = AsyncMongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["users"]

    async def getAllUsers(self) -> list[UserModel]:    
        cursor = self.collection.find({})
        users_raw = await cursor.to_list(length=100)
        return [UserModel(**user) for user in users_raw]
    
    async def getUser(self, username) -> Optional[UserModel]:
        user_dict = await self.collection.find_one({"_id": username})
        if user_dict:
            return UserModel(**user_dict)  # <-- Return the Model
        return None
    
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
        
    async def delUser(self, username) -> Optional[UserModel]:
        deleted_user_dict = await self.collection.find_one_and_delete({"_id": username})
        if deleted_user_dict:
            return UserModel(**deleted_user_dict)
        return None