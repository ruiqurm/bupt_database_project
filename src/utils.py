from pydantic import BaseModel
from typing import Any, Iterator, Callable, TypedDict, TypeVar, Union, List

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

def batch(it: Iterator, size):
    return iter(lambda: tuple(islice(it, size)), ())


async def fetch_one(command: str, *args, connection: Union[None, asyncpg.Connection] = None) -> asyncpg.Record:
    """获取一条
    如果提供connection，不会关闭连接
    Args:
        command (str): _description_
        connection (Union[None,asyncpg.Connection], optional): _description_. Defaults to None.

    Returns:
        asyncpg.Record: _description_
    """
    if connection is None:
        connection = await asyncpg.connect(user=Settings.DEFAULT_USER, database=Settings.DEFAULT_DATABASE)
        result = await connection.fetchrow(command, *args)
        await connection.close()
    else:
        result = await connection.fetch(command, *args)
    return result


async def fetch_all(command: str, *args, connection: Union[None, asyncpg.Connection] = None) -> List[asyncpg.Record]:
    """获取多条
    如果提供connection，不会关闭连接

    Args:
        command (str): _description_
        connection (Union[None,asyncpg.Connection], optional): _description_. Defaults to None.

    Returns:
        List[asyncpg.Record]: _description_
    """
    if connection is None:
        connection = await asyncpg.connect(user=Settings.DEFAULT_USER, database=Settings.DEFAULT_DATABASE)
        result = await connection.fetch(command, *args)
        await connection.close()
    else:
        result = await connection.fetch(command, *args)
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
