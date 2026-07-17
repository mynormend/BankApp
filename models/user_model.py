# models/user_model.py
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    id: str = Field(alias="_id")
    fname: str
    lname: str
    email: str
    password: str
    role: str = "user"

    model_config = {
        "populate_by_name": True,
    }