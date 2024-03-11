from fastapi import FastAPI
import uvicorn
from models.model import DataSchema

app = FastAPI()


data = [
    {
    "id": 1,
    "name": "mayank",
    "age": "21",
    "email": "mayankrai@gmail.com"
    },
    {
    "id": 2,
    "name": "anuj",
    "age": "19",
    "email": "bing@gmail.com"
    }
]


@app.get("/", tags = ["greet"])
def greet():
    return {
        "Hello": "Mayank"
    }
    
@app.get("/data", tags = ["data"])
def fetch_all_data():
    return {"data": data}

@app.get("/data/{id}", tags = ["data"])
def fetch_one_data(id: int):
    if id > len(data):
        return {"Invalid id"}
    for d in data:
        if d["id"] == id:
            return {"Single_data": d}
    return {"data not found"}