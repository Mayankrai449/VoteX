import time
import jwt
from decouple import config


JWT_SECRET = config("secret_key")
JWT_ALGORITHM = config("algorithm")

def return_token(token: str):
    return {
        "jwt_token": token
    }
    
def signJWT(userID: str):
    payload = {
        "userID": userID,
        "expiry": time.time() + 600
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return return_token(token)

def decodeJWT(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decoded_token if decoded_token["expiry"] >= time.time() else None
    except:
        return {}