# service.py
from repo.user_repo import UserRepo

class UserService():
    def __init__(self):
        self.repo = UserRepo()

    async def getAllUsers(self):
        return await self.repo.getAllUsers()
    
    async def addUser(self,username, fname, lname, email, passwd):
        return await self.repo.addUser(username, fname, lname, email, passwd)
    
    async def delUser(self, username):
        return await self.repo.delUser(username)