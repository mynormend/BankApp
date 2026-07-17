# models/user_model.py
from pydantic import BaseModel, Field
from typing import Optional

class UserModel(BaseModel):
    id: str = Field(alias="_id")  # MongoDB's unique identifier
    fname: str
    lname: str
    email: str
    password: str
    role: str = "user"

    model_config = {
        "populate_by_name": True,
    }