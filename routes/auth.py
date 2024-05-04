from fastapi import APIRouter, Request, Response, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated


from datetime import timedelta
import control
import auth


from models.model import UserRegSchema
from main import db

router = APIRouter()


router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@router.get("/register", response_class=HTMLResponse, tags=["data"])
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/user/register", tags=["user"])
async def user_register(user: UserRegSchema = Depends(UserRegSchema.form)):
    try:
        data = user.model_dump()
        data["password"] = auth.get_hashed_password(data["password"])
        data["age"] = control.calculate_age(data["dob"])
        db.users.insert_one(data)
        return RedirectResponse(url="/login")
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/login", tags = ["greet"])
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
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response