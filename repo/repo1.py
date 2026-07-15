# repo.py

class repo():
    def __init__(self):
        self.users = {123: {"userID": 123, 
                  "fname": "Mynor", 
                  "lname": "Mendez"
            }
        }
        self.next_user_id = 124

    def getAllUsers(self):
        return list(self.users.values())
    
    
    def addUser(self, fname, lname):
        user = {
            "userID": self.next_user_id,
            "fname": fname,
            "lname": lname,
        }
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user        

    def delUser(self, userID):
        return self.users.pop(userID,None)