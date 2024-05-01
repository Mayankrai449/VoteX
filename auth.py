
from fastapi.security import OAuth2PasswordBearer
from typing import Union
from jose import jwt
from passlib.context import CryptContext

from typing import Union
from typing_extensions import Annotated
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from decouple import config

from models.model import UserLoginSchema
from models.database import get_database_connection

db = get_database_connection()

pass_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="login")
JWT_SECRET = config("secret_key")
JWT_ALGORITHM = config("algorithm")
TOKEN_TIME = 15


def check_user(data: UserLoginSchema):
    users = db.users.find({})
    for user in users:
        if user["username"] == data.username:
            if verify_password(data.password, user["password"]):
                return True
    return False

def get_user(username: str):
    user = db.users.find_one({"username": username})
    if user:
        user_data = {key: value for key, value in user.items() if key != "_id"}
        return user_data
    return None

def verify_password(plain_password, hashed_password):
    return pass_context.verify(plain_password, hashed_password)

def get_hashed_password(password):
    return pass_context.hash(password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TIME)
    
    to_encode.update({"exp": expire, "username": to_encode["sub"]})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt
