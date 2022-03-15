
from fastapi import Request, Depends
from .user_token import oauth2_scheme, ALGORITHM, SECRET_KEY, TokenData
from .user import UserInDB
from .exceptions import InactiveUser, Unauthorization, PermissionDenied, NoSuchUser
from jose import JWTError, jwt
from typing import List
import asyncpg


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> UserInDB:
    """获取访问url的用户，中间件

    Args:
            request (Request): _description_
            token (str, optional): token字符串

    Raises:
            NoSuchUser: 没有这个用户
            Unauthorization: 密码错误
            InactiveUser: 用户未激活

    Returns:
            UserInDB: 用户对象
    """
    try:
        # 校验jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("bupt")
        if username is None:
            raise NoSuchUser()
        # 查询用户数据
        token_data = TokenData(username=username)
        con = await asyncpg.connect(user='postgres', database="tb")
        user = await con.fetchrow('SELECT * FROM "USER" WHERE "username"= $1', token_data.username)
        await con.close()
    except JWTError:
        raise Unauthorization()
    if user is None:
        raise NoSuchUser()
    user: UserInDB = UserInDB(**user)
    if not user.is_active:
        raise InactiveUser()
    # 保存到request的上下文
    request.state.user = user
    return user


async def check_admin(user: UserInDB = Depends(get_current_user)):
    """判断当前用户是否是管理员

    Args:
            user (UserInDB, optional): 用户对象

    Raises:
            PermissionDenied: 权限不足
    """
    if not user.is_admin:
        raise PermissionDenied()
