
from fastapi import APIRouter
import asyncpg
from pydantic import BaseModel
from src.user import User

from src.utils import fetch_all, fetch_one, get_connection
from ..settings import Settings,ValidUploadTableName
debug_router = APIRouter(
    prefix=f"/debug",
    tags=["debug"],
)
class Command(BaseModel):
	cmd : str
@debug_router.post("/exec")
async def exec_cmd(cmd:Command):
	try:
		connection = await get_connection()
		result = await connection.fetch(cmd)
		await connection.close()
		return result
	except Exception as e:
		return e

@debug_router.delete("/table")
async def exec_cmd(table:ValidUploadTableName):
	try:
		connection = await get_connection()
		await connection.execute(f'delete from "{table}"')
		await connection.close()
	except Exception as e:
		return e


@debug_router.post("/asadmin")
async def asadmin(id:int):
	"""
	把用户设置为管理员

	Args:
		id (int): id

	"""
	try:
		await fetch_one('update "USER" set "is_admin" = true,"is_active"= true where "id" = $1',id)
		return "ok"
	except Exception as e:
		return e

@debug_router.get("/user")
async def listuser():
	"""
	查看用户

	Args:
		id (int): id

	"""
	users = await fetch_all('SELECT * FROM "USER"')
	return [User(**user) for user in users]
