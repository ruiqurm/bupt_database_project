"""
处理关于user的路由
"""
from ..user import UserIn, user_create,User
from ..exceptions import Unauthorization
from ..utils import CommonResponse
from ..user_token import Token, authenticate_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from ..dependency import get_current_user,check_admin
from fastapi import APIRouter
from fastapi import Depends
from datetime import datetime, timedelta
from typing import Optional,List
import aiosqlite

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
    """
    注册用户
    """
    user.password = get_password_hash(user.password)
    await user_create(user)
    return {}


@normal_router.post("/login", response_model=Token)
async def login(data: UserIn):
    """
    登录
    """
    # 验证用户密码
    user = await authenticate_user(data.username, data.password)
    if not user:
        raise Unauthorization()
    # 签发token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
from fastapi import Request

@user_router.get("/me", response_model=User)
async def read_users_me(request:Request):
    return request.state.user

@admin_router.get("/user", response_model=List[User])
async def get_users():
    async with aiosqlite.connect("./user.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM USER') as cursor:
            rows = await cursor.fetchall()
            if rows:
                return [User(**row) for row in rows]
            else:
                return []
    

@admin_router.post("/administrator/{userid}")
async def grant_user_as_admin(userid:int):
    async with aiosqlite.connect("./user.db") as db:
        await db.execute("UPDATE USER SET is_admin = true WHERE id = ?", (userid,))
        await db.commit()

@admin_router.delete("/administrator/{userid}")
async def revoke_user_as_admin(userid:int):
    async with aiosqlite.connect("./user.db") as db:
        await db.execute("UPDATE USER SET is_admin = false WHERE id = ?", (userid,))
        await db.commit()

@admin_router.post("/active/{userid}")
async def activate_user(userid:int):
    async with aiosqlite.connect("./user.db") as db:
        await db.execute("UPDATE USER SET is_active = true WHERE id = ?", (userid,))
        await db.commit()

@admin_router.delete("/active/{userid}")
async def deactivate_user(userid:int):
    async with aiosqlite.connect("./user.db") as db:
        await db.execute("UPDATE USER SET is_active = false WHERE id = ?", (userid,))
        await db.commit()
        