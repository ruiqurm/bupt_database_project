import asyncio
import asyncpg
async def run():
	pool = await asyncpg.create_pool(user='postgres', host='127.0.0.1',database='tb')
	async with pool.acquire() as con:
		print(await con.fetch(
		'SELECT * FROM "USER"'))

loop = asyncio.get_event_loop()
loop.run_until_complete(run())