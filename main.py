# main.py
import dotenv
from fastapi import FastAPI
from controller.user_controller import router as user_router
from controller.bank_controller import router as bank_router
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()
origin = os.getenv("VITE_API_URL")

app = FastAPI()
app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(bank_router, prefix="/bank", tags=["Banking & Ledger"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def main(): 
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__": 
    main() 