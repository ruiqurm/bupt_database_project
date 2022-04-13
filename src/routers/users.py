"""
处理关于user的路由
"""
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm

from src.utils import fetch_one
from ..user import UserIn, User
from ..exceptions import OperationFailed
from ..user_token import Token, authenticate_user, get_password_hash, create_access_token
from ..dependency import get_current_user, check_admin
from ..settings import Settings
from fastapi import APIRouter
from fastapi import Depends
from datetime import datetime, timedelta
import asyncpg

user_router = APIRouter(
    prefix="/user",
    tags=["user相关"],
    dependencies=[Depends(get_current_user)],
)
normal_router = APIRouter(
    tags=["user相关"],
)



@normal_router.post("/register")
async def register(user: UserIn):
    """注册用户
    密码要8位

    Args:
        user (UserIn): 注册表单，JSON格式

    Raises:
        CreateFailed: 注册失败异常

    Returns:
        User: 注册成功的用户
    """
    user.password = get_password_hash(user.password)
    try:
        await fetch_one('INSERT INTO myuser ("username", "password") VALUES ($1,$2)',user.username, user.password)
    except asyncpg.PostgresError as e:
        raise OperationFailed()
    return User(** await fetch_one('SELECT * FROM myuser WHERE "username"= $1',user.username))


@normal_router.post("/token", response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    """login代理接口，用于接入openapi，方便调试

    Args:
        form_data (OAuth2PasswordRequestForm, optional): _description_. Defaults to Depends().
    """
    return await login(UserIn(username=form_data.username, password=form_data.password))


@normal_router.post("/login")
async def login(data: UserIn):
    """登录

    Args:
        data (UserIn): 登录表单，JSON格式

    Raises:
        Unauthorization: 密码错误
        NoSuchUser: 没有这个用户
        InactiveUser: 这个用户没有激活
    Returns:
        Token: 令牌
    """
    # 验证用户密码
    user = await authenticate_user(data.username, data.password)
    # 签发token
    access_token_expires = timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={Settings.PAYLOAD_NAME: user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer",**user.dict()}


@user_router.get("/me", response_model=User)
async def read_users_me(request: Request):
    """返回用户信息

    Returns:
        User: 除密码外的信息
    """
    return request.state.user


