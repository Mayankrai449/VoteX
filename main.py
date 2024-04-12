from fastapi import FastAPI, Body, Form, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from typing import Union
from typing_extensions import Annotated, Doc
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from decouple import config

import uvicorn
from models.model import UserRegSchema, UserLoginSchema, TokenData, Token, UserPass
from models.poll_model import PollForm
import control


pass_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="login")
JWT_SECRET = config("secret_key")
JWT_ALGORITHM = config("algorithm")
TOKEN_TIME = 15

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

conn = MongoClient("mongodb+srv://Mayankrai449:RWHLI4g2RqoHljpQ@cluster0.7hu8wbd.mongodb.net/votingsys")
db = conn.votingsys

def check_user(data: UserLoginSchema):
    users = db.users.find({})
    for user in users:
        if user["username"] == data.username:
            if verify_password(data.password, user["password"]):
                return True
    return False

def get_user(username: str):
    user = db.users.find_one({"username": username})
    return user

def verify_password(plain_password, hashed_password):
    return pass_context.verify(plain_password, hashed_password)

def get_hashed_password(password):
    return pass_context.hash(password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TIME)
    
    to_encode.update({"exp": expire, "username": to_encode["sub"]})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

    

@app.get("/", tags = ["greet"])
async def greet(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/layout", response_class=HTMLResponse, tags=["greet"])
async def layout(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})

    
@app.get("/register", response_class=HTMLResponse, tags=["data"])
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/data/{username}", tags=["data"])
def get_one_user(username: str):
    data = db.users.find_one({"username": username})
    name =  data["fullname"]
    return {"fullname": name}

@app.get("/dashboard", tags=["data"])
async def dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "token": current_user})


@app.post("/register", tags=["user"])
async def user_register(user: UserRegSchema = Depends(UserRegSchema.form)):
    try:
        data = user.model_dump()
        data["password"] = get_hashed_password(data["password"])
        db.users.insert_one(data)
        return RedirectResponse(url="/login")
    except Exception as e:
        return {"error": str(e)}

@app.post("/createpoll", tags = ["poll"])
async def create_poll(data: PollForm = Depends(PollForm.form)):
    try:
        poll = data.model_dump()
        db.polls.insert_one(poll)
        return {"message": "Poll created successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/pollform", response_class=HTMLResponse, tags=["poll"])
async def poll_form(request: Request):
    return templates.TemplateResponse("createpoll.html", {"request": request})

@app.post("/login", tags=["user"])
async def user_login(response: Response, user: OAuth2PasswordRequestForm = Depends()):
    if not check_user(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"})
        
    access_token_expires = timedelta(minutes=TOKEN_TIME)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}
    
    
if __name__ == "__main__":
    uvicorn.run(app, port=8004, host="127.0.0.1")