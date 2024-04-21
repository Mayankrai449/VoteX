from fastapi import FastAPI, Body, Form, Depends, HTTPException, status, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm

from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import Union
from typing_extensions import Annotated
from datetime import datetime, timedelta, timezone
import pytz
from urllib.parse import urlencode
from event_handlers import register_event_handlers
from bson.codec_options import CodecOptions

import auth
from dependencies import get_current_active_user

import uvicorn
from models.model import UserRegSchema
from models.poll_model import PollForm
import control

register_event_handlers()

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
    
local_timezone = pytz.timezone('Asia/Kolkata')

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
        end_datetime_str = f"{data.end_date} {data.end_time}"
        end_datetime = datetime.strptime(end_datetime_str, "%m/%d/%Y %H:%M")
        
        end_datetime_local = local_timezone.localize(end_datetime)
        
        poll = data.model_dump()
        poll["creator"] = current_user["username"]
        poll["poll_id"] = control.encode_id(poll["title"], poll["creator"])
        poll["expiry_time"] = end_datetime_local
        
        db.polls.insert_one(poll)
        db.polls.create_index("expiry_time", expireAfterSeconds=0)
        
        return {"message": "Poll created successfully"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/pollform", tags=["poll"])
async def poll_form(request: Request, current_user: dict = Depends(get_current_active_user)):
    return templates.TemplateResponse("createpoll.html", {"request": request, "token": current_user})


@app.get("/polls", tags=["poll"])
async def get_polls(request: Request, current_user: dict = Depends(get_current_active_user)):
    polls = db.polls.find({"creator": current_user["username"]})
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


@app.post("/vote/{poll_id}", status_code=201, tags=["poll"])
async def vote(response: Response, poll_id: str, cast: Annotated[str, Form()], current_user: dict = Depends(get_current_active_user)):
    username = current_user["username"]
    poll = db.polls.find_one({"poll_id": poll_id})
    user = db.users.find_one({"username": username})
    votes = db.votes.find_one({"poll_id": poll_id, "voter": username})
    
    if votes:
        raise HTTPException(status_code=400, detail="You have already voted in this poll")
    
    if user["age"] < poll["age"]:
        raise HTTPException(status_code=400, detail="You are not eligible to vote in this poll")
    
    data = {
        "poll_id": poll_id,
        "creater": poll["creator"],
        "voter": username,
        "vote": cast
    }
    
    db.votes.insert_one(data)
    
    query_params = urlencode({"cast": cast})
    redirect_url = f"/updatevote/{poll_id}?{query_params}"
    
    response = RedirectResponse(url=redirect_url)
    return response


@app.post("/updatevote/{poll_id}", tags=["poll"])
async def update_vote(poll_id: str, cast: str = Query(..., alias="cast"), current_user: dict = Depends(get_current_active_user)):
    poll = db.polls.find_one({"poll_id": poll_id})
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    if cast not in poll["name"]:
        raise HTTPException(status_code=400, detail="Invalid vote")
    poll["name"][cast] += 1
    
    db.polls.update_one({"poll_id": poll_id}, {"$set": {"name": poll["name"]}})
    
    return RedirectResponse(url=f"/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.patch("/updatepoll/{poll_id}", tags=["poll"])
async def update_poll(poll_id: str, data: PollForm = Depends(PollForm.form), current_user: dict = Depends(get_current_active_user)):
    poll = db.polls.find_one({"poll_id": poll_id})
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    db.polls.update_one({"poll_id": poll_id}, {"$set": data.model_dump()})
    return RedirectResponse(url=f"/poll/{poll_id}", status_code=status.HTTP_303_SEE_OTHER)


@app.delete("/deletepoll/{poll_id}", tags=["poll"])
async def delete_poll(poll_id: str, current_user: dict = Depends(get_current_active_user)):
    poll = db.polls.find_one({"poll_id": poll_id})
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    db.polls.delete_one({"poll_id": poll_id})
    return RedirectResponse(url="/polls", status_code=status.HTTP_303_SEE_OTHER)
    
    

@app.get("/register", response_class=HTMLResponse, tags=["data"])
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/user/register", tags=["user"])
async def user_register(user: UserRegSchema = Depends(UserRegSchema.form)):
    try:
        data = user.model_dump()
        data["password"] = auth.get_hashed_password(data["password"])
        data["age"] = control.calculate_age(data["dob"])
        db.users.insert_one(data)
        return RedirectResponse(url="/login")
    except Exception as e:
        return {"error": str(e)}

@app.post("/login", tags=["user"])
async def token_auth(response: Response, user: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if not auth.check_user(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=auth.TOKEN_TIME)
    access_token = auth.create_access_token(
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