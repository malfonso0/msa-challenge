from datetime import datetime, timedelta, timezone
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from model import Lista, ListaCreate
from database import get_db
from sqlmodel import Session
from typing import List
import logging

from model.security import TokenData, Token

security_router = APIRouter(tags=["security"])

###### security ######
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from model import User, hash_verify,UserBase
from sqlmodel import select
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # update to use this one on hash_xxx
oauth2_scheme  = OAuth2PasswordBearer(tokenUrl="/token")

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # simple example! make new one!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

db_dependency = Annotated[Session, Depends(get_db)]

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(session, username: str):
    statement = select(User).where(User.email == username)
    user = session.exec(statement).first()
    return user

def authenticate_user(session, username: str, password: str):
    user = get_user(session, username)
    if not user:
        return False
    if not hash_verify(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                        session:db_dependency)->User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session, token_data.username)
    if user is None:
        raise credentials_exception
    return user

user_dependency= Annotated[User, Depends(get_current_user)]

@security_router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                session : db_dependency)-> Token:
    user = authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@security_router.get("/current", response_model=UserBase)
async def read_users_me(current_user:user_dependency):
    
    data = current_user.dict()
    user = UserBase.model_validate(data)
    return user

class RoleChecker:  
    def __init__(self, allowed_roles:list[str]):  
        self.allowed_roles = allowed_roles  

    def __call__(self, user: user_dependency):  
        logging.info("checking user: %s has roles %s", user.email, self.allowed_roles)

        if any(role.nombre in self.allowed_roles for role in user.roles):
            return True  

        raise HTTPException(  
            status_code=status.HTTP_401_UNAUTHORIZED,   
            detail="No tiene permisos para realizar esta operacion"
        )

admin_user_dependency = Depends(RoleChecker(allowed_roles=["Admin"]))
uploader_user_dependency = Depends(RoleChecker(allowed_roles=["Admin", "Uploader"]))
writer_user_dependency =  Depends(RoleChecker(allowed_roles=["Admin", "Writer"]))
reader_user_dependency = Depends(RoleChecker(allowed_roles=["Admin", "Reader"]))

