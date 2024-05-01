from fastapi import FastAPI, Body, Form, Depends, HTTPException, status, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Cookie
from models.database import get_database_connection

from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import Union, Optional, Dict, Any
from typing_extensions import Annotated
from datetime import datetime, timedelta, timezone
import pytz
from urllib.parse import urlencode

import auth
from dependencies import get_current_active_user

import uvicorn
from models.model import UserRegSchema
from models.poll_model import PollForm
import control


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

local_timezone = pytz.timezone('Asia/Kolkata')


@app.get("/layout", response_class=HTMLResponse, tags=["greet"])
async def layout(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})

@app.get("/dashboard", tags=["data"])
async def dashboard(request: Request, current_user: dict = Depends(get_current_active_user),
                    flash_message: Optional[str] = Cookie(None),
                    flash_type: Optional[str] = Cookie(None)):
    response = templates.TemplateResponse("dashboard.html", {"request": request, "token": current_user,
                                                             "user": current_user["username"],
                                                             "flash_message": flash_message,
                                                             "flash_type": flash_type})
    response.set_cookie(key="flash_message", value="", httponly=True)
    response.set_cookie(key="flash_type", value="", httponly=True)
    
    return response

@app.get("/history", tags=["data"])
async def history(request: Request, current_user: dict = Depends(get_current_active_user)):
    
    history = db.history.find({"creator": current_user["username"], "poll_id": {"$nin": db.polls.distinct("poll_id")}})
    
    return templates.TemplateResponse("history.html", {"request": request, "history": history, "token": current_user})

@app.get("/results", tags=["data"])
async def all_res(request: Request, current_user: dict = Depends(get_current_active_user)):
    
    res = db.votes.find({"voter": current_user["username"], "poll_id": {"$nin": db.polls.distinct("poll_id")}})
    
    poll_ids = [r["poll_id"] for r in res]
    
    results = db.history.find({"poll_id": {"$in": poll_ids}})
    
    return templates.TemplateResponse("allResults.html", {"request": request, "results": results, "token": current_user})

@app.get("/results/{poll_id}", tags=["data"], response_class=HTMLResponse)
async def result(request: Request, poll_id: str, current_user: dict = Depends(get_current_active_user)):
    
    results = db.history.find_one({"poll_id": poll_id})
    
    vote_counts: Dict[str, int] = {}
    for candidate, count in results['name'].items():
        vote_counts[candidate] = vote_counts.get(candidate, 0) + count

    winner = max(vote_counts, key=vote_counts.get) if vote_counts else None

    data: Dict[str, Any] = {"request": request, "results": results, "vote": vote_counts, "winner": winner, "token": current_user}
    
    return templates.TemplateResponse("result.html", data)

@app.post("/createpoll", tags=["poll"])
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
        
        db.history.insert_one(poll)
        
        response = RedirectResponse(url="/polls", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="flash_message", value="Poll created successfully!", httponly=True)
        response.set_cookie(key="flash_type", value="success", httponly=True)
        
        return response
    except Exception as e:
        response = RedirectResponse(url="/pollform", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="flash_message", value=str(e), httponly=True)
        response.set_cookie(key="flash_type", value="failure", httponly=True)
        return response


@app.get("/pollform", tags=["poll"])
async def poll_form(request: Request, current_user: dict = Depends(get_current_active_user)):
    return templates.TemplateResponse("createpoll.html", {"request": request, "token": current_user})


@app.get("/polls", tags=["poll"])
async def get_polls(request: Request, current_user: dict = Depends(get_current_active_user),
                    flash_message: Optional[str] = Cookie(None),
                    flash_type: Optional[str] = Cookie(None)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    polls = db.polls.find({"creator": current_user["username"]})
    response = templates.TemplateResponse("allPolls.html", {"request": request,
                                                        "polls": polls, "token": current_user,
                                                        "flash_message": flash_message,
                                                        "flash_type": flash_type})
    response.set_cookie(key="flash_message", value="", httponly=True)
    response.set_cookie(key="flash_type", value="", httponly=True)
    
    return response

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
    poll_in_polls = db.polls.find_one({"poll_id": poll_id})
    poll_in_history = db.history.find_one({"poll_id": poll_id})

    if not poll_in_polls or not poll_in_history:
        raise HTTPException(status_code=404, detail="Poll not found")

    if cast not in poll_in_polls["name"]:
        raise HTTPException(status_code=400, detail="Invalid vote")
    
    poll_in_polls["name"][cast] += 1
    db.polls.update_one({"poll_id": poll_id}, {"$set": {"name": poll_in_polls["name"]}})

    if cast not in poll_in_history["name"]:
        raise HTTPException(status_code=400, detail="Invalid vote")
    
    poll_in_history["name"][cast] += 1
    db.history.update_one({"poll_id": poll_id}, {"$set": {"name": poll_in_history["name"]}})
    
    return RedirectResponse(url=f"/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.patch("/updatepoll/{poll_id}", tags=["poll"])
async def update_poll(poll_id: str, data: PollForm = Depends(PollForm.form), current_user: dict = Depends(get_current_active_user)):
    poll = db.polls.find_one({"poll_id": poll_id})
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    db.polls.update_one({"poll_id": poll_id}, {"$set": data.model_dump()})
    return RedirectResponse(url=f"/poll/{poll_id}", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/deletepoll/{poll_id}", tags=["poll"])
async def delete_poll(response: Response, poll_id: str, current_user: dict = Depends(get_current_active_user)):
    poll = db.polls.find_one({"poll_id": poll_id})
    response = RedirectResponse(url="/polls", status_code=status.HTTP_303_SEE_OTHER)
    if not poll:
        flash_message = "Poll Not Found!"
        flash_type = "failure"

        return response
    
    db.polls.delete_one({"poll_id": poll_id})
    flash_message = "Poll Deleted Successfully!"
    flash_type = "success"
    
    response.set_cookie(key="flash_message", value=flash_message, httponly=True)
    response.set_cookie(key="flash_type", value=flash_type, httponly=True)
    
    return response
    
    

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
    
@app.get("/login", tags = ["greet"])
async def login(request: Request, message: str = None):
    flash_message = None
    flash_type = None
    
    if message == "expired":
        flash_message = "Session expired. Please login again"
        flash_type = "neutral"
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "flash_message": flash_message, 
        "flash_type": flash_type})

@app.post("/user/login", tags=["user"])
async def token_auth(response: Response, user: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if not auth.check_user(user):
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        flash_message = "Incorrect username or password"
        flash_type = "failure"
    else:
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        flash_message = "Login Successful!"
        flash_type = "success"
        
    access_token_expires = timedelta(minutes=auth.TOKEN_TIME)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    response.set_cookie(key="flash_message", value=flash_message, httponly=True)
    response.set_cookie(key="flash_type", value=flash_type, httponly=True)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    
    return response
    
@app.get("/logout", tags=["user"])
def logout(response: Response):
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
    
if __name__ == "__main__":
    uvicorn.run(app, port=8004, host="127.0.0.1")