"""
处理关于user的路由
"""
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from ..user import UserIn, User
from ..exceptions import OperationFailed
from ..user_token import Token, authenticate_user, get_password_hash, create_access_token
from ..dependency import get_current_user, check_admin
from ..settings import Settings
from fastapi import APIRouter
from fastapi import Depends
from datetime import datetime, timedelta
from typing import Optional, List
import asyncpg

user_router = APIRouter(
    prefix="/user",
    tags=["user相关"],
    dependencies=[Depends(get_current_user)],
)
normal_router = APIRouter(
    tags=["user相关"],
)
admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(check_admin)]
)


@normal_router.post("/register")
async def register(user: UserIn):
    """注册用户

    Args:
        user (UserIn): 注册表单，JSON格式

    Raises:
        CreateFailed: 注册失败异常

    Returns:
        None: 注册成功
    """
    user.password = get_password_hash(user.password)
    try:
        con = await asyncpg.connect(user=Settings.DEFAULT_USER, database=Settings.DEFAULT_DATABASE)
        await con.execute('INSERT INTO "USER" ("username", "password") VALUES ($1,$2)', user.username, user.password)
        await con.close()
    except asyncpg.PostgresError as e:
        raise OperationFailed()
    return {}


@normal_router.post("/token", response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    """login代理接口，用于接入openapi，方便调试

    Args:
        form_data (OAuth2PasswordRequestForm, optional): _description_. Defaults to Depends().
    """
    return await login(UserIn(username=form_data.username, password=form_data.password))


@normal_router.post("/login", response_model=Token)
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
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/me", response_model=User)
async def read_users_me(request: Request):
    """返回用户信息

    Returns:
        User: 除密码外的信息
    """
    return request.state.user


@admin_router.get("/user", response_model=List[User])
async def get_users():
    """获取所有用户，需要管理员权限

    Returns:
        List[User]: 所有用户的信息
    """
    con = await asyncpg.connect(user=Settings.DEFAULT_USER, database=Settings.DEFAULT_DATABASE)
    users = await con.fetch('SELECT * FROM "USER"')
    await con.close()
    return [User(**user) for user in users]


@admin_router.post("/administrator/{userid}")
async def grant_user_as_admin(userid: int):
    """授予用户管理员权限，需要管理员权限
    即使用户不存在也不会报错

    Args:
        userid (int): 用户id
    """
    con = await asyncpg.connect(user=Settings.DEFAULT_USER, database=Settings.DEFAULT_DATABASE)
    await con.execute('UPDATE "USER" SET is_admin = true WHERE id = $1', userid)
    await con.close()


@admin_router.delete("/administrator/{userid}")
async def revoke_user_as_admin(userid: int):
    """撤销用户管理员权限，需要管理员权限
    即使用户不存在也不会报错

    Args:
        userid (int): 用户id
    """
    con = await asyncpg.connect(user=Settings.DEFAULT_USER, database=Settings.DEFAULT_DATABASE)
    await con.execute('UPDATE "USER" SET is_admin = false WHERE id = $1', userid)
    await con.close()


@admin_router.post("/active/{userid}")
async def activate_user(userid: int):
    """激活用户，需要管理员权限
    即使用户不存在也不会报错

    Args:
        userid (int): 用户id
    """
    con = await asyncpg.connect(user=Settings.DEFAULT_USER, database=Settings.DEFAULT_DATABASE)
    await con.execute('UPDATE "USER" SET is_active = true WHERE id = $1', userid)
    await con.close()


@admin_router.delete("/active/{userid}")
async def deactivate_user(userid: int):
    """反激活用户，需要管理员权限
    即使用户不存在也不会报错

    Args:
        userid (int): 用户id
    """
    con = await asyncpg.connect(user=Settings.DEFAULT_USER, database=Settings.DEFAULT_DATABASE)
    await con.execute('UPDATE "USER" SET is_active = false WHERE id = $1', userid)
    await con.close()
