from fastapi import APIRouter
from fastapi import Depends
from typing import Optional, List

import pydantic
from ..dependency import check_admin
from ..user import User
from src.utils import fetch_all, fetch_one, fetch_one_then_wrap_model
admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    # dependencies=[Depends(check_admin)]
)


@admin_router.get("/user", response_model=List[User])
async def get_users():
    """获取所有用户，需要管理员权限

    Returns:
        List[User]: 所有用户的信息
    """
    users = await fetch_all('SELECT * FROM myuser')
    return [User(**user) for user in users]


@admin_router.post("/administrator/{userid}")
async def grant_user_as_admin(userid: int):
    """授予用户管理员权限，需要管理员权限
    即使用户不存在也不会报错

    Args:
        userid (int): 用户id
    """
    await fetch_one('UPDATE myuser SET is_admin = true WHERE id = $1', userid)
    return "ok"


@admin_router.delete("/administrator/{userid}")
async def revoke_user_as_admin(userid: int):
    """撤销用户管理员权限，需要管理员权限
    即使用户不存在也不会报错

    Args:
        userid (int): 用户id
    """
    await fetch_one('UPDATE myuser SET is_admin = false WHERE id = $1', userid)
    return "ok"


@admin_router.post("/active/{userid}")
async def activate_user(userid: int):
    """激活用户，需要管理员权限
    即使用户不存在也不会报错

    Args:
        userid (int): 用户id
    """
    await fetch_one('UPDATE myuser SET is_active = true WHERE id = $1', userid)
    return "ok"


@admin_router.delete("/active/{userid}")
async def deactivate_user(userid: int):
    """反激活用户，需要管理员权限
    即使用户不存在也不会报错

    Args:
        userid (int): 用户id
    """
    await fetch_one('UPDATE myuser SET is_active = false WHERE id = $1', userid)
    return "ok"

class TableInfo(pydantic.BaseModel):
    table_name : str
    size_pretty :str
    size : int
    path : str
    tuple_count :int

class SharedBuffer(pydantic.BaseModel):
    pass

@admin_router.get("/database/",response_model=List[TableInfo])
async def get_table_info():
    """获取数据库信息

    """
    table_info_command = """
    SELECT 
    table_name, 
    pg_size_pretty( pg_total_relation_size(quote_ident(table_name)))as size_pretty, 
    pg_total_relation_size(quote_ident(table_name)) as size,
    pg_relation_filepath(CAST(table_name AS text)) as path,
    n_live_tup as tuple_count
    FROM 
    information_schema.tables
    INNER JOIN pg_stat_user_tables ON table_name = relname
    WHERE 
    table_schema = 'public'
    ORDER BY 
    pg_total_relation_size(quote_ident(table_name)) DESC;
    """
    return [TableInfo(**i) for i in await fetch_all(table_info_command)]