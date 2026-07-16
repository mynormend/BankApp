# main.py
from fastapi import FastAPI
from controller.user_controller import router as user_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def main(): 
    return 0

if __name__ == "__main__": 
    main() 