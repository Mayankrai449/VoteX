from fastapi import Form, Depends, HTTPException, status, Request, Query, APIRouter
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Cookie

from typing import Optional, Dict, Any
from urllib.parse import urlencode
from typing_extensions import Annotated

from main import db
from models.poll_model import PollForm

from dependencies import get_current_active_user
from datetime import datetime
import pytz

import control


router = APIRouter()

local_timezone = pytz.timezone('Asia/Kolkata')

router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@router.post("/createpoll", tags=["poll"])
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


@router.get("/pollform", tags=["poll"])
async def poll_form(request: Request, current_user: dict = Depends(get_current_active_user)):
    return templates.TemplateResponse("createpoll.html", {"request": request, "token": current_user})


@router.get("/polls", tags=["poll"])
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

@router.get("/poll/{poll_id}", tags=["poll"])
async def get_poll(request: Request, poll_id: str, current_user: dict = Depends(get_current_active_user)):
    poll = db.polls.find_one({"poll_id": poll_id})
    name = poll["name"]
    return templates.TemplateResponse("poll.html", {"request": request, "poll": poll, "name": name, "token": current_user})


@router.post("/vote", tags=["poll"])
async def vote(response: Response, poll_id: Annotated[str, Form()], current_user: dict = Depends(get_current_active_user)):
    poll = db.polls.find_one({"poll_id": poll_id})
    if not poll:
        return {"error": "Poll not found"}
    return RedirectResponse(url=f"/poll/{poll_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/vote/{poll_id}", status_code=201, tags=["poll"])
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


@router.post("/updatevote/{poll_id}", tags=["poll"])
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


@router.patch("/updatepoll/{poll_id}", tags=["poll"])
async def update_poll(poll_id: str, data: PollForm = Depends(PollForm.form), current_user: dict = Depends(get_current_active_user)):
    poll = db.polls.find_one({"poll_id": poll_id})
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    db.polls.update_one({"poll_id": poll_id}, {"$set": data.model_dump()})
    return RedirectResponse(url=f"/poll/{poll_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/deletepoll/{poll_id}", tags=["poll"])
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