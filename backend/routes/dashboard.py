from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Cookie

from typing import Optional, Dict, Any

from models.database import get_database_connection
from models.model import User

from controller.dependencies import get_current_active_user


router = APIRouter()

router.mount("/backend/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="templates")

# @router.get("/userdata", response_model=User)
# async def get_user(current_user: dict = Depends(get_current_active_user), db = Depends(get_database_connection)):
#     email = db.users.find_one({"username": current_user["username"]})
#     user_data = {
#         "user": current_user["username"],
#         "email": email["email"]
#     }
#     return user_data

@router.get("/userdata")
async def get_user():
    data = {
        "user": "Mink",
        "email": "mayankraivns@gmail.com"
    }
    return data

@router.get("/dashboard", tags=["data"])
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

@router.get("/history", tags=["data"])
async def history(request: Request, current_user: dict = Depends(get_current_active_user), db = Depends(get_database_connection)):
    
    history = db.history.find({"creator": current_user["username"], "poll_id": {"$nin": db.polls.distinct("poll_id")}})
    
    return templates.TemplateResponse("history.html", {"request": request, "user": current_user["username"], "history": history, "token": current_user})

@router.get("/results", tags=["data"])
async def all_res(request: Request, current_user: dict = Depends(get_current_active_user), db = Depends(get_database_connection)):
    
    res = db.votes.find({"voter": current_user["username"], "poll_id": {"$nin": db.polls.distinct("poll_id")}})
    
    poll_ids = [r["poll_id"] for r in res]
    
    results = db.history.find({"poll_id": {"$in": poll_ids}})
    
    return templates.TemplateResponse("allResults.html", {"request": request, "user": current_user["username"], "results": results, "token": current_user})

@router.get("/results/{poll_id}", tags=["data"], response_class=HTMLResponse)
async def result(request: Request, poll_id: str, current_user: dict = Depends(get_current_active_user), db = Depends(get_database_connection)):
    
    results = db.history.find_one({"poll_id": poll_id})
    
    vote_counts: Dict[str, int] = {}
    for candidate, count in results['name'].items():
        vote_counts[candidate] = vote_counts.get(candidate, 0) + count

    winner = max(vote_counts, key=vote_counts.get) if vote_counts else None

    data: Dict[str, Any] = {"request": request, "user": current_user["username"], "results": results, "vote": vote_counts, "winner": winner, "token": current_user}
    
    return templates.TemplateResponse("result.html", data)