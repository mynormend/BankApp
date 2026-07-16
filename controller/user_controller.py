# user_controller.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from service.user_service import UserService

user_Service = UserService()


class userResponse(BaseModel):
    username: str = Field(alias="_id")
    fname: str
    lname: str
    email: str
    model_config = {
        "populate_by_name": True,
    }

class userCreateRequest(BaseModel):
    username: str
    fname: str
    lname: str
    email: str
    passwd: str

router = APIRouter()

@router.get("/users", response_model=list[userResponse])    
async def get_users():
    return await user_Service.getAllUsers()


@router.post("/users", response_model=userResponse, status_code=201)
async def add_user(user: userCreateRequest):
    return await user_Service.addUser(user.username, user.fname, user.lname, user.email, user.passwd)

@router.delete("/users/{username}", response_model=userResponse, status_code=200)
async def delete_user(username: str):
    deleted_user = await user_Service.delUser(username)

    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found") 
    return deleted_user