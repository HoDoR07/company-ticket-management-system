import os
from dotenv import load_dotenv
from jose import jwt,JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI,Body,status,HTTPException,Depends,Request
from . import database,models

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp":expire
    })

    encoded_jwt =jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm = ALGORITHM
    )

    return encoded_jwt

token_collect = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(token = Depends(token_collect), db = Depends(database.get_db)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid token")

        current_user = db.query(models.User).filter(models.User.id == user_id).first()

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail="Unauthorized Access")
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail="Unauthorized Access")        
    return current_user




# def get_current_user_raw(request:Request, db = Depends(database.get_db)):
#     token = request.headers.get("authorization")
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Unauthorized Access")

#     if not token.startswith("Bearer"):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Unauthorized Access")
#     auth = token.split(" ")[1]
#     try:
#         payload = jwt.decode(
#             auth,
#             SECRET_KEY,
#             algorithms=[ALGORITHM]
#         )
#         user_id = payload["user_id"]
#         current_user = db.query(models.User).filter(models.User.id == user_id).first()
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Unauthorized Access")
#     if not current_user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Unauthorized Access")

#     return current_user




## Authorization 

def require_role(allowed_role,current_user = Depends(get_current_user)):
    if not current_user.role == allowed_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return current_user

def technician_only(current_user = Depends(get_current_user)):
    return require_role("technician",current_user)

def admin_only(current_user = Depends(get_current_user)):
    return require_role("admin",current_user)