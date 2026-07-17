# user_controller.py
from typing_extensions import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from service.user_service import UserService, UserAlreadyExistsException, UserNotFoundException
from service.auth_service import AuthService

user_Service = UserService()
auth_service = AuthService(user_Service)

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

class userCreateRequest(BaseModel):
    username: str
    fname: str
    lname: str
    email: str
    passwd: str
    role: Literal["admin", "user"] = "user"

class LoginRequest(BaseModel):
    username: str
    password: str

# Token response schema
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# API endpoint to fetch all users, returns a list of userResponse models
@router.get("/users", response_model=list[userResponse])    
async def get_users():
    user_models = await user_Service.getAllUsers()
    # Dump each model into a raw dictionary, preserving the '_id' field
    return [user.model_dump(by_alias=True) for user in user_models]

# API endpoint to fetch a specific user by username, returns a userResponse model
@router.get("/users/{username}", response_model=userResponse)
async def get_user(username: str):
    try:
        user_model = await user_Service.getUser(username)
        # Convert the individual UserModel to a dictionary preserving the '_id' alias
        return user_model.model_dump(by_alias=True)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

# API endpoint to add a new user, returns the created userResponse model
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
        return user_model.model_dump(by_alias=True)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=str(e))

# API endpoint to delete a user by username, returns the deleted userResponse model
@router.delete("/users/{username}", response_model=userResponse, status_code=200)
async def delete_user(username: str):
    try:
        user_model = await user_Service.delUser(username)
        return user_model.model_dump(by_alias=True)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

    
@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    try:
        user = await auth_service.authenticate_user(
        username=credentials.username, 
        password=credentials.password
        )
        token_payload = {
            "sub": user.id,      # Unique subject identity
            "role": user.role    # Access permissions group
        }
        token = auth_service.create_access_token(data=token_payload)
        
        return TokenResponse(access_token=token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication service error")