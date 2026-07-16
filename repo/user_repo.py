# repo.py
from pymongo import AsyncMongoClient
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
uri = os.getenv("MONGO_URL")
db_name = os.getenv("MONGODB_DB")


class UserRepo():
    def __init__(self):
        self.client = AsyncMongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["users"]

    async def getAllUsers(self):    
        cursor = self.collection.find({})
        return await cursor.to_list(length=100)
    
    async def addUser(self, username, fname, lname, email, passwd):
        new_user = {
            "_id": username,  # ensure the username is the unique ID in the collection
            "fname": fname,
            "lname": lname,
            "email": email,
            "password": passwd
        }
        await self.collection.insert_one(new_user)
        return new_user
        
    async def delUser(self, username):
        deleted_user = await self.collection.find_one_and_delete({"_id": username})
        return deleted_user