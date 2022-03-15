
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Any,Optional,Dict
from datetime import datetime, timedelta
from .user import UserInDB
from .exceptions import NoSuchUser,InactiveUser,Unauthorization
from jose import jwt
import asyncpg
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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
    con = await asyncpg.connect(user='postgres', database="tb")
    user = await con.fetchrow('SELECT * FROM "USER" WHERE "username"= $1',username)
    await con.close()
    if user is None:
        raise NoSuchUser()
    user: UserInDB = UserInDB(**user)
    # 验证用户是否有效
    if not user or not user.is_active:
        raise InactiveUser()
    # 验证用户密码是否正确
    if not pwd_context.verify(password, user.password):
        raise Unauthorization()
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
