from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt, ExpiredSignatureError
from models.model import TokenData
import auth  # Assuming auth module contains the necessary functions

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.JWT_SECRET, algorithms=[auth.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except ExpiredSignatureError:
        message = "expired"
        return RedirectResponse(url="/login", status_code=302, headers={"Location": f"/login?message={message}"})
    except JWTError:
        raise credentials_exception

    user = auth.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user