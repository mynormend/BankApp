# user_controller.py
from typing_extensions import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from service.user_service import UserService, UserAlreadyExistsException, UserNotFoundException

user_Service = UserService()
router = APIRouter()

# Data transfered from the server to the client
class userResponse(BaseModel):
    username: str = Field(alias="_id")
    fname: str
    lname: str
    email: str
    role: str
    model_config = {
        "populate_by_name": True,
    }

# Data transfered from the client to the server
class userCreateRequest(BaseModel):
    username: str
    fname: str
    lname: str
    email: str
    passwd: str
    role: Literal["admin", "user"] = "user"


@router.get("/users", response_model=list[userResponse])    
async def get_users():
    # Fetch clean domain models from the service layer
    user_models = await user_Service.getAllUsers()
    # Dump each model into a raw dictionary, preserving the '_id' field alias
    return [user.model_dump(by_alias=True) for user in user_models]


@router.get("/users/{username}", response_model=userResponse)
async def get_user(username: str):
    try:
        user_model = await user_Service.getUser(username)
        # Convert the individual UserModel to a dictionary preserving the '_id' alias
        return user_model.model_dump(by_alias=True)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/users", response_model=userResponse, status_code=201)
async def add_user(user: userCreateRequest):
    try:
        user_model = await user_Service.addUser(
            username=user.username, 
            fname=user.fname, 
            lname=user.lname, 
            email=user.email, 
            passwd=user.passwd,
            role=user.role
        )
        # Convert the newly created UserModel to a dictionary preserving the '_id' alias
        return user_model.model_dump(by_alias=True)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/users/{username}", response_model=userResponse, status_code=200)
async def delete_user(username: str):
    try:
        user_model = await user_Service.delUser(username)
        # Convert the deleted UserModel to a dictionary preserving the '_id' alias
        return user_model.model_dump(by_alias=True)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))