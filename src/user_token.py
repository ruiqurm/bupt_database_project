
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Any,Optional,Dict
from datetime import datetime, timedelta

from src.utils import fetch_all, fetch_one
from .user import UserInDB
from .exceptions import NoSuchUser,InactiveUser,Unauthorization, ValidateError
from jose import jwt
import asyncpg
from .settings import Settings


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = await fetch_one('SELECT * FROM myuser WHERE "username" = $1',username)
    if user is None:
        raise NoSuchUser()
    user: UserInDB = UserInDB(**user)
    # 验证用户是否有效
    if not user or not user.is_active:
        raise InactiveUser()
    # 验证用户密码是否正确
    if not pwd_context.verify(password, user.password):
        raise ValidateError()
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)
    return encoded_jwt
