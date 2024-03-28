from pydantic import BaseModel, Field, EmailStr
from fastapi import Form

    
class UserRegSchema(BaseModel):
    fullname: str
    email: EmailStr
    dob: str = Field(default=None),
    city: str = Field(default=None),
    password: str
    
    @classmethod
    def form(cls,
                fullname: str = Form(...),
                email: EmailStr = Form(...),
                dob: str = Form(...),
                city: str = Form(...),
                password: str = Form(...)
    ):
        return cls(
            fullname=fullname,
            email=email,
            dob=dob,
            city=city,
            password=password
        )
    
 
class UserLoginSchema(BaseModel):
    email: EmailStr = Field(default=None),
    password: str = Field(default=None),
    
    @classmethod
    def form(cls,
                email: EmailStr = Form(...),
                password: str = Form(...)
    ):
        return cls(
            email=email,
            password=password
        )