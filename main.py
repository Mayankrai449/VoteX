from fastapi import FastAPI, Body, Form, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import Union
from typing_extensions import Annotated
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    if user:
        user_data = {key: value for key, value in user.items() if key != "_id"}
        return user_data
    return None

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

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
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

async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

    

@app.get("/", tags = ["greet"])
async def greet(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/layout", response_class=HTMLResponse, tags=["greet"])
async def layout(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})


@app.get("/data/{username}", tags=["data"])
def get_one_user(username: str):
    data = db.users.find_one({"username": username})
    name =  data["fullname"]
    return {"fullname": name}

@app.get("/dashboard", tags=["data"])
async def dashboard(request: Request, current_user: dict = Depends(get_current_active_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "token": current_user})


@app.post("/createpoll", tags = ["poll"])
async def create_poll(data: PollForm = Depends(PollForm.form), current_user: dict = Depends(get_current_active_user)):
    try:
        poll = data.model_dump()
        poll["username"] = current_user["username"]
        poll["poll_id"] = control.encode_id(poll["title"], poll["username"])
        db.polls.insert_one(poll)
        return {"message": "Poll created successfully"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/pollform", tags=["poll"])
async def poll_form(request: Request, current_user: dict = Depends(get_current_active_user)):
    return templates.TemplateResponse("createpoll.html", {"request": request, "token": current_user})

@app.get("/polls", tags=["poll"])
async def get_polls(request: Request, current_user: dict = Depends(get_current_active_user)):
    polls = db.polls.find({"username": current_user["username"]})
    return templates.TemplateResponse("allPolls.html", {"request": request, "polls": polls, "token": current_user})

@app.get("/poll/{poll_id}", tags=["poll"])
async def get_poll(request: Request, poll_id: str, current_user: dict = Depends(get_current_active_user)):
    poll = db.polls.find_one({"poll_id": poll_id})
    name = poll["name"]
    return templates.TemplateResponse("poll.html", {"request": request, "poll": poll, "name": name, "token": current_user})

@app.post("/vote", tags=["poll"])
async def vote(response: Response, poll_id: Annotated[str, Form()], current_user: dict = Depends(get_current_active_user)):
    poll = db.polls.find_one({"poll_id": poll_id})
    if not poll:
        return {"error": "Poll not found"}
    return RedirectResponse(url=f"/poll/{poll_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/vote/{poll_id}", tags=["poll"])
async def vote(response: Response, poll_id: str, cast: Annotated[str, Form()], current_user: dict = Depends(get_current_active_user)):
    username = current_user["username"]
    poll = db.polls.find_one({"poll_id": poll_id})
    user = db.users.find_one({"username": username})
    votes = db.votes.find_one({"poll_id": poll_id, "username": username})
    
    if votes:
        raise HTTPException(status_code=400, detail="You have already voted in this poll")
    
    if user["age"] < poll["age"]:
        raise HTTPException(status_code=400, detail="You are not eligible to vote in this poll")
    
    data = {
        "poll_id": poll_id,
        "username": username,
        "vote": cast
    }
    
    db.votes.insert_one(data)
    
    return {"message": "Vote cast successfully", "poll_id": poll_id, "vote": cast}
    
    
    


@app.get("/register", response_class=HTMLResponse, tags=["data"])
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/user/register", tags=["user"])
async def user_register(user: UserRegSchema = Depends(UserRegSchema.form)):
    try:
        data = user.model_dump()
        data["password"] = get_hashed_password(data["password"])
        data["age"] = control.calculate_age(data["dob"])
        db.users.insert_one(data)
        return RedirectResponse(url="/login")
    except Exception as e:
        return {"error": str(e)}

@app.post("/login", tags=["user"])
async def token_auth(response: Response, user: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if not check_user(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=TOKEN_TIME)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response
    
@app.get("/logout", tags=["user"])
def logout(response: Response):
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
    
if __name__ == "__main__":
    uvicorn.run(app, port=8004, host="127.0.0.1")