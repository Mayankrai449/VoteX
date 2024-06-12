from fastapi import APIRouter, Request, Response, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated

from fastapi import Cookie
from typing import Optional

from datetime import timedelta
from controller.utils import calculate_age
import auth

from models.model import UserRegSchema
from models.database import get_database_connection


router = APIRouter()


router.mount("/backend/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="templates")

@router.get("/register", response_class=HTMLResponse, tags=["data"])
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/user/register", tags=["user"])
async def user_register(user: UserRegSchema = Depends(UserRegSchema.form), db = Depends(get_database_connection)):
    try:
        data = user.model_dump()
        data["password"] = auth.get_hashed_password(data["password"])
        data["age"] = calculate_age(data["dob"])
        db.users.insert_one(data)
        return RedirectResponse(url="/login")
    except Exception as e:
        return {"error": str(e)}
    
    
    if message != "expired":
        response.set_cookie(key="flash_message", value="", httponly=True)
        response.set_cookie(key="flash_type", value="", httponly=True)
    
    return response

@router.post("/user/login", tags=["user"])
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
    
@router.get("/logout", tags=["user"])
def logout(response: Response):  
    response.delete_cookie("access_token")
    
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    flash_message = "You have been Successfully Logged Out!"
    flash_type = "success"
    
    response.set_cookie(key="flash_message", value=flash_message, httponly=True)
    response.set_cookie(key="flash_type", value=flash_type, httponly=True)
    
    return response