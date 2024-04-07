from fastapi import FastAPI, Body, Form, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from typing import Annotated
from pydantic import BaseModel, Field, EmailStr

import uvicorn
from models.model import UserRegSchema, UserLoginSchema
from models.poll_model import PollForm
from auth.jwt_handler import signJWT
from auth.jwt_bearer import jwtBearer
import control


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

conn = MongoClient("mongodb+srv://Mayankrai449:RWHLI4g2RqoHljpQ@cluster0.7hu8wbd.mongodb.net/votingsys")
db = conn.votingsys


@app.get("/", tags = ["greet"])
def greet(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/layout", response_class=HTMLResponse, tags=["greet"])
def layout(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})

    
@app.get("/register", response_class=HTMLResponse, tags=["data"])
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/data/{email}", tags=["data"])
def get_one_user(email: EmailStr):
    data = conn.votingsys.users.find_one({"email": email})
    name =  data["fullname"]
    return {"fullname": name}

@app.get("/dashboard", response_class=HTMLResponse, dependencies=[Depends(jwtBearer())], tags=["data"])
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/user/register", tags=["user"])
async def user_register(user: UserRegSchema = Depends(UserRegSchema.form)):
    try:
        data = user.model_dump()
        conn.votingsys.users.insert_one(data)
        return RedirectResponse(url="/user/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        return {"error": str(e)}

def check_user(data: UserLoginSchema):
    users = conn.votingsys.users.find({})
    for user in users:
        if user["email"] == data.email:
            if user["password"] == data.password:
                return True
    return False

@app.post("/createpoll", tags = ["poll"])
async def create_poll(data: PollForm = Depends(PollForm.form)):
    try:
        poll = data.model_dump()
        conn.votingsys.polls.insert_one(poll)
        return {"message": "Poll created successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/pollform", response_class=HTMLResponse, tags=["poll"])
async def poll_form(request: Request):
    return templates.TemplateResponse("createpoll.html", {"request": request})

@app.post("/user/login", response_class=HTMLResponse, tags=["user"])
async def user_login(response: Response, user: UserLoginSchema = Depends(UserLoginSchema.form)):
    if check_user(user):
        token = signJWT(user.email)
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    
if __name__ == "__main__":
    uvicorn.run(app, port=8004, host="127.0.0.1")