from pydantic import BaseModel, Field, EmailStr
from datetime import date

class DataSchema(BaseModel):
    id: int = Field(default=None),
    name: str = Field(default=None),
    age: int = Field(default=None),
    email: EmailStr = Field(default=None),
    

class UserRegSchema(BaseModel):
    fullname: str
    email: EmailStr
    dob: str = Field(default=None),
    city: str = Field(default=None),
    password: str
    
 
class UserLoginSchema(BaseModel):
    email: EmailStr = Field(default=None),
    password: str = Field(default=None),
    