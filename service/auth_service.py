# auth_service.py
import bcrypt
from datetime import datetime, timedelta, timezone
import jwt
from os import getenv
from service.user_service import UserService, UserNotFoundException
from models.user_model import UserModel
from typing import Optional

class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    # Authenticate user credentials against stored hashed passwords
    async def authenticate_user(self, username: str, password: str) -> Optional[UserModel]:
        try:
            user = await self.user_service.getUser(username)
        except UserNotFoundException:
            return None
        
        # String-encoded variables to binary formats for cryptographic validation
        stored_password_bytes = user.password.encode('utf-8')
        input_password_bytes = password.encode('utf-8')

        # Bcrypt verifies if the input plain text matches the database hash safely
        if not bcrypt.checkpw(input_password_bytes, stored_password_bytes):
            return None
            
        return user
    
    # Generate a JWT token for authenticated users with an expiration time of 10 minutes
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        minutes = int(getenv("JWT_EXPIRE_MINUTES", "10"))
        
        # Add a time-to-live expiration milestone
        expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        to_encode.update({"exp": expire})
        
        # Sign the token using your environment secret key configuration
        encoded_jwt = jwt.encode(
            to_encode, 
            getenv("JWT_SECRET_KEY"), 
            algorithm=getenv("JWT_ALGORITHM")
        )
        return encoded_jwt
    
    # Decode and validate the JWT token, returning the payload if valid
    def decode_token(self, token: str) -> Optional[dict]:
        try:
            # Unpack payload and verify that the signature has not been tampered with
            payload = jwt.decode(
                token, 
                getenv("JWT_SECRET_KEY"), 
                algorithms=[getenv("JWT_ALGORITHM")]
            )
            return payload
        except jwt.InvalidTokenError:
            return None