"""
用户
"""
# import aiosqlite
from .exceptions import ValidateError
from pydantic import BaseModel, validator
import re
from typing import Any, Optional, Dict

USERNAME_MAX_LENGTH = 32
USERNAME_MIN_LENGTH = 4
PASSWORD_MAX_LENGTH = 16
PASSWORD_MIN_LENGTH = 8
USERNAME_RULE = re.compile("^[a-zA-Z\d\!@#$%\^&\*\(\)~`,.;'\x20]*$")
PASSWORD_RULE = re.compile("^[a-zA-Z\d\!@#$%\^&\*\(\)~`,.;'\x20]*$")


class UserIn(BaseModel):
    """用于登录，注册的用户信息
    """
    username: str
    password: str

    @validator('username')
    def validate_name(cls, v: str):
        if len(v) < USERNAME_MIN_LENGTH or len(v) > USERNAME_MAX_LENGTH or USERNAME_RULE.match(v) is None:
            raise ValidateError("用户名不合法")
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < PASSWORD_MIN_LENGTH or len(v) > PASSWORD_MAX_LENGTH or PASSWORD_RULE.match(v) is None:
            raise ValidateError("密码不合法")
        return v


class User(BaseModel):
    """能看到的用户信息
    """
    id: int
    username: str
    is_active: Optional[bool] = None
    is_admin: bool = False


class UserInDB(User):
    """数据库中的用户信息
    """
    password: str
