"""
用户
"""
import aiosqlite
from .exceptions import ValidateError,CreateFailed
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
    id: int
    username: str
    is_active: Optional[bool] = None
    is_admin: bool = False


class UserInDB(User):
    password: str


"""
暂用的用户数据库
"""


async def user_get_by_name(name: str) -> UserInDB:
    async with aiosqlite.connect("./user.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM USER WHERE username = "{}"'.format(name)) as cursor:
            row = await cursor.fetchone()
            if row:
                return UserInDB(**row)
            else:
                return None


async def user_get_by_id(id: int) -> UserInDB:
    async with aiosqlite.connect("./user.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM USER WHERE id = ?', (id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return UserInDB(**row)
            else:
                return None


async def user_create(user: UserInDB):
	async with aiosqlite.connect("./user.db") as db:
		try:
			await db.execute("""
			INSERT INTO USER (username, password)
			VALUES (?, ?)
			""", (user.username, user.password))
			await db.commit()
		except sqlite3.Error as e:
			raise CreateFailed()

async def user_update(user: UserInDB):
    async with aiosqlite.connect("./user.db") as db:
        await db.execute("""
		UPDATE USER
		SET username = ?, password = ?, is_active = ?, is_admin = ?
		WHERE id = ?
		""", (user.username, user.password, user.is_active, user.is_admin, user.id))
        await db.commit()


async def user_remove(id: int):
    async with aiosqlite.connect("user.db") as db:
        await db.execute("""
		DELETE FROM USER WHERE id = ?
		""", (id,))
        await db.commit()

"""
引入时自动执行脚本
"""

import sqlite3

db = sqlite3.connect("user.db")
db.cursor().execute("""
CREATE TABLE IF NOT EXISTS USER (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username VARCHAR(32) NOT NULL UNIQUE,
	password CHAR(64) NOT NULL,
	is_active BOOL NOT NULL DEFAULT TRUE,
	is_admin BOOL NOT NULL DEFAULT FALSE
);
""")
db.commit()
