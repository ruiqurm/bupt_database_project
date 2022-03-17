
from fastapi import APIRouter
import asyncpg
from pydantic import BaseModel

from src.utils import get_connection
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