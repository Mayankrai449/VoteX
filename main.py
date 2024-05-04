from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from models.database import get_database_connection

from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware


import uvicorn


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

db = get_database_connection()


    
if __name__ == "__main__":
    uvicorn.run(app, port=8004, host="127.0.0.1")