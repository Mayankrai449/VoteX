from fastapi import FastAPI, Body, Depends, HTTPException, status
import uvicorn
from models.model import DataSchema, UserRegSchema, UserLoginSchema
from auth.jwt_handler import signJWT
from auth.jwt_bearer import jwtBearer
import config


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

users = []


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

@app.post("/post", dependencies=[Depends(jwtBearer())], tags=["posts"])
def post_data(data_set: DataSchema):
    data_set.id = len(data) + 1
    data.append(data_set.model_dump())
    return {"data posted!"}

@app.post("/user/register", tags=["user"])
def user_register(user: UserRegSchema = Body(default=None)):
    user.id = len(users) + 1
    user.age = config.calculate_age(user.dob)
    users.append(user)
    return signJWT(user.email)

def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email:
            if user.password == data.password:
                return True
    return False

@app.post("/user/login", tags=["user"])
def user_login(user: UserLoginSchema = Body(default=None)):
    if check_user(user):
        return {"message": "Logged in!"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
