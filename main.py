# main.py
from fastapi import FastAPI
from controller.user_controller import router as user_router

app = FastAPI()
app.include_router(user_router)


def main(): 
    return 0

if __name__ == "__main__": 
    main() 