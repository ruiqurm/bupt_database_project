# import asyncpg
# pool = None
# def get_pool():
# 	global pool
# 	return pool
# async def init_databasepool():
# 	global pool # 取database.py的pool变量
# 	if pool is not None:
# 		del pool
# 	pool = await asyncpg.create_pool(user='postgres', host='127.0.0.1',database='tb')