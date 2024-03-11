from pydantic import BaseModel, Field, EmailStr
from datetime import date

class DataSchema(BaseModel):
    id: int = Field(default=None),
    name: str = Field(default=None),
    age: int = Field(default=None),
    email: EmailStr = Field(default=None),
    
    class config:
        external_ref = {
            "demo": {
                "id": 1,
                "name": "mayank",
                "age": 21,
                "email": "raimayank@gmail.com"
            }
        }


class UserRegSchema(BaseModel):
    id: int = Field(default=None),
    fullname: str = Field(default=None),
    dob: date = Field(default=None),
    age: int = Field(default=None),
    email: EmailStr = Field(default=None),
    city: str = Field(default=None),
    password: str = Field(default=None),
    
    class config:
        external_ref = {
            "demo": {
                "id": 1,
                "fullname": "mayank",
                "dob": date(2000, 1, 1),
                "age": 24,
                "email": "sample@email.com",
                "city": "delhi",
                "password": "pass123"
            }
        }
 
class UserLoginSchema(BaseModel):
    email: EmailStr = Field(default=None),
    password: str = Field(default=None),
    
    class config:
        external_ref = {
            "demo": {
                "username": "mayank",
                "password": "pass123"
            }
        }