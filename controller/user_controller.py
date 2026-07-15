# controller.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from service.service import userService

user_Service = userService()


class userResponse(BaseModel):
    userID: str = Field(alias="_id")
    fname: str
    lname: str

    model_config = {
        "populate_by_name": True,
    }

class userCreateRequest(BaseModel):
    fname: str
    lname: str
    email: str
    passwd: str

class userDeleteRequest(BaseModel):
    userID: str

router = APIRouter()

@router.get("/users", response_model=list[userResponse])    
async def getUsers():
    return await user_Service.getAllUsers()


@router.post("/users", response_model=userResponse, status_code=201)
async def addUser(user: userCreateRequest):
    return await user_Service.addUser(user.fname, user.lname, user.email, user.passwd)

@router.delete("/users", response_model=userResponse, status_code=200)
async def delUser(userID: str):
    deleted_user = user_Service.delUser(userID)
    
    if not deleted_user:
        raise HTTPException(status_code=405, detail="User not found")
        
    return await deleted_user