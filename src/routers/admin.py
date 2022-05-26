
from gettext import translation
from http.client import HTTPException
from fastapi import APIRouter
from typing import Any, Optional, List
import fastapi

import pydantic
from ..user import User
from src.utils import fetch_all, fetch_one, fetch_one_then_wrap_model, get_connection
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

class PostgresSettingShortcut(pydantic.BaseModel):
    shared_buffers :Optional[int] = None
    wal_buffers : Optional[int] = None
    effective_cache_size : Optional[int] = None
    maintenance_work_mem : Optional[int] = None
    max_connections :Optional[int] = None
    tcp_keepalives_idle:Optional[int] = None

class PostgresSettingShortcutOutput(pydantic.BaseModel):
    name : str
    setting : int
    unit : Optional[str]
    inbytes : Optional[int] = None
    default : int 
    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.unit:
            if self.unit == "s":
                self.inbytes = self.setting
            elif self.unit.endswith("kB"):
                if len(self.unit)==2:
                    self.inbytes = self.setting * 1024
                else:
                    self.inbytes = int(self.unit[:-2]) * 1024
            else:
                self.inbytes = None
        else:
            self.unit = ""
            self.inbytes = self.setting
    

@admin_router.get("/postgres/database/",response_model=List[TableInfo])
async def get_table_info():
    """获取数据表信息

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

@admin_router.post("/postgres/basic")
async def set_postgres_basic(settings:PostgresSettingShortcut):
    """
    shared_buffers PostgreSQL自身的缓冲区  
    wal_buffers 将其WAL（预写日志）记录写入缓冲区，然后将这些缓冲区刷新到磁盘。如果有大量并发连接的话，则设置为一个较高的值可以提供更好的性能。  
    effective_cache_size  提供可用于磁盘高速缓存的内存量的估计值。  
    maintenance_work_mem 用于维护任务的内存设置。  
    max_connections 最大连接数  
    tcp_keepalives_idle 客户端超时时间  
    """

    command = "select name,setting,unit,reset_val as \"default\" from pg_settings where name in ('shared_buffers','wal_buffers','effective_cache_size','maintenance_work_mem','max_connections','tcp_keepalives_idle');"
    origin = {item.name:item.default for item in [PostgresSettingShortcutOutput(**i) for i in await fetch_all(command)]}
    changed = 0
    try:
        for key in settings.__fields__.keys():
            value = getattr(settings, key)
            if value is None:
                continue
            changed+=1
            if value < 0 :
                value = "default"
            command = "ALTER SYSTEM SET {} = {};".format(key,value)
            await fetch_one(command)
        if changed > 0:
            command = "SELECT pg_reload_conf();"
            await fetch_one(command)
    except Exception as e: 
        for key in settings.__fields__.keys():
            command = "ALTER SYSTEM SET {} = {};".format(key,origin[key])
            await fetch_one(command)
        command = "SELECT pg_reload_conf();"
        
        await fetch_one(command)
        raise fastapi.HTTPException(detail=str(e),status_code=400) 
    return changed
@admin_router.get("/postgres/basic",response_model=List[PostgresSettingShortcutOutput])
async def get_postgres_basic():
    """
    获取shared_buffers，wal_buffers，effective_cache_size等数据
    """
    command = "select name,setting,unit,reset_val as \"default\" from pg_settings where name in ('shared_buffers','wal_buffers','effective_cache_size','maintenance_work_mem','max_connections','tcp_keepalives_idle');"
    return [PostgresSettingShortcutOutput(**i) for i in await fetch_all(command)]

import os 

@admin_router.get("/postgres/config")
async def get_config():
    command = "SHOW config_file;"
    path = await fetch_one(command)
    path = path["config_file"]
    path = path.replace("postgresql.conf","postgresql.auto.conf")
    if not os.path.exists(path):
        return []
    try:
        with open(path,"r") as file:
            return [i for i in file.read().split("\n") if not i.startswith("#") and i != ""]
    except Exception as e:
        return str(e)