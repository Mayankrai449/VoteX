from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from auth.jwt_handler import decodeJWT

class jwtBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(jwtBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials: HTTPAuthorizationCredentials = await super(jwtBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid or Expired token!")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid or Expired token!")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid or Expired token!")
    
    def verify_jwt(self, jwt_token: str):
        token_validity: bool = False
        
        payload = decodeJWT(jwt_token)
        if payload:
            token_validity = True
            
        return token_validity
