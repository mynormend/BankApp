# service.py
from repo.repo import repo

class userService():
    def __init__(self):
        self.repo = repo()

    async def getAllUsers(self):
        return await self.repo.getAllUsers()
    
    async def addUser(self, fname, lname, email, passwd):
        return await self.repo.addUser(fname, lname, email, passwd)
    
    async def delUser(self, userID):
        return await self.repo.delUser(userID)