from pydantic import BaseModel
from typing import Any, Iterator, Callable, TypedDict, TypeVar, Union,List

from itertools import zip_longest, islice
import asyncpg
from .settings import Settings


class CommonResponse(BaseModel):
    code: int
    msg: str
    data: Any = None


def grouper(n: int, iterable):
    # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks?page=2&tab=modifieddesc#tab-top
    return zip_longest(*[iter(iterable)]*n)


# def batch(size: int, it: Iterator):
#     while item := list(islice(it, size)):
#         yield item

def batch(it:Iterator, size):
    return iter(lambda: tuple(islice(it, size)), ())

async def fetch_one(command: str, *args) -> asyncpg.Record:
    connection = await asyncpg.connect(user=Settings.DEFAULT_USER, database=Settings.DEFAULT_DATABASE)
    result = await connection.fetchrow(command, *args)
    await connection.close()
    return result
async def fetch_all(command: str, *args) -> List[asyncpg.Record]:
    connection = await asyncpg.connect(user=Settings.DEFAULT_USER, database=Settings.DEFAULT_DATABASE)
    result = await connection.fetch(command, *args)
    await connection.close()
    return result
R = TypeVar('R')


async def fetch_one_then_wrap_model(command: str, model: Callable[[TypedDict], R], *args) -> Union[R, None]:
    connection = await asyncpg.connect(user=Settings.DEFAULT_USER, database=Settings.DEFAULT_DATABASE)
    result = await connection.fetchrow(command, *args)
    await connection.close()
    if result is not None:
        return model(**result)
    else:
        return {}
