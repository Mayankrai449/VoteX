from pydantic import BaseModel, Field, EmailStr

class DataSchema(BaseModel):
    id: int = None,
    name: str = None,
    age: int = None,
    email: str = None,
    class config():
        external_ref = {
            "id": 1,
            "name": "mayank",
            "email": "raimayank@gmail.com"
        }