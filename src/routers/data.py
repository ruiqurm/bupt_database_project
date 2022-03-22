import os
from ..pylouvain import PyLouvain, in_order
from fastapi.responses import FileResponse
from calendar import month
import uuid
from fastapi import BackgroundTasks
import fastapi
from ..utils import batch, fetch_all, fetch_one, fetch_one_then_wrap_model, get_connection
import datetime
from pydantic import BaseModel
import sqlite3
from fastapi import APIRouter, File, UploadFile
# import aiofiles
from enum import Enum
from ..exceptions import OperationFailed
from ..settings import ValidTableName, ValidUploadTableName, get_insert_command, Settings, transform_type
from typing import List, Optional, Dict
import csv

data_router = APIRouter(
    prefix=f"{Settings.DATA_ROUTER_PREFIX}",
    tags=["data"],
)


class UploadTask(BaseModel):
    id: str
    done: bool = False
    failed: bool = False
    msg: str = ""
    current_row: int = 0


__upload_dict = dict()


async def upload_data_background(id: str, reader: csv.reader, table_name: str, command: str, max_line: int):
    """后台上传

    Args:
        reader (csv.reader): _description_
        table_name (str): _description_
        command (str): _description_
    """
    counter = 0
    connection = await get_connection()
    try:
        async with connection.transaction():
            for fifty_rows in batch(iter(reader), max_line):
                # 没做触发器
                counter += max_line
                await connection.executemany(command, [transform_type(table_name, i) for i in fifty_rows])
                __upload_dict[id].current_row = counter
    except Exception as e:
        __upload_dict[id].msg = str(e)
        __upload_dict[id].failed = True
    finally:
        __upload_dict[id].done = True


@data_router.post("/upload")
async def upload_data(table: ValidUploadTableName, file: UploadFile, background_tasks: BackgroundTasks, encoding: str = "utf-8", max_line: int = 50):
    """上传数据

    Args:
        table (ValidUploadTableName): 表名
        file (UploadFile): 文件
        encoding (str, optional): 文件编码. 默认为 "utf-8".
        max_line: 一次最大操作行
    Raises:
        : 上传文件失败异常

    Returns:
        _type_: _description_
    """
    contents = await file.read()
    data = contents.decode(encoding).splitlines()
    # file.file._file = io.TextIOBase(file.file._file,encoding="utf-8")
    reader = csv.reader(data, delimiter=',', quotechar='"')
    command = get_insert_command(table)

    # 执行插入操作
    next(reader)  # skip title
    id = uuid.uuid4().hex
    __upload_dict[id] = UploadTask(id=id)
    background_tasks.add_task(upload_data_background,
                              id, reader, table, command, max_line)

    return {"id": id, "url": f"{Settings.DATA_ROUTER_PREFIX}/upload/status?id={id}"}


@data_router.get("/upload/status")
def upload_status(id: str):
    """获取上传状态

    Args:
        id (str): _description_

    Raises:
        fastapi.HTTPException: _description_

    Returns:
        _type_: _description_
    """
    if id in __upload_dict:
        return __upload_dict[id]
    raise fastapi.HTTPException(status_code=404, detail="Item not found")


__download_dict = dict()


@data_router.get("/download")
async def download_table(table: ValidTableName):
    """请求准备下载
    """
    table_name = table.name
    connection = await get_connection()
    if table_name in __download_dict:
        for file in __download_dict[table_name]:
            os.remove(f"{Settings.TEMPDIR}/{file}")
    __download_dict[table_name] = []
    async with connection.transaction():
        count = await connection.fetchrow(f'SELECT COUNT(*) FROM "{table_name}"')
        count = count["count"]
        max_row = Settings.MAX_ROW_PER_FILE
        for i in range(0, count, max_row):
            id = uuid.uuid4().hex + ".csv"
            command = f'COPY (select * from "{table_name}" LIMIT {max_row} OFFSET {i}) TO \'{Settings.TEMPDIR}/{id}\' WITH (FORMAT CSV, HEADER);'
            # print(command)
            await connection.execute(command)
            __download_dict[table_name].append(id)
    return ["/data/download/file?id={}".format(file) for file in __download_dict[table_name]]


@data_router.get("/download/file")
async def download_table_file(id: str):
    file = os.path.join(Settings.TEMPDIR, id)
    return FileResponse(path=file, filename=id)


class GetSectorEnocdeChoice(str, Enum):
    name = "name"
    id = "id"


# @data_router.get("/{category}")
# async def get_sector_list(category:SectorOrEnocde,choice: GetSectorEnocdeChoice):
# 	if category==SectorOrEnocde.sector and choice == GetSectorEnocdeChoice.name:
# 		command = "SELECT SECTOR_NAME From tbCell GROUP BY SECTOR_NAME"
# 	elif category==SectorOrEnocde.sector and choice == GetSectorEnocdeChoice.id:
# 		command = "SELECT SECTOR_ID From tbCell GROUP BY SECTOR_ID"
# 	elif category==SectorOrEnocde.enodeb and choice == GetSectorEnocdeChoice.name:
# 		command = "SELECT ENODEB_NAME From tbCell GROUP BY ENODEB_NAME"
# 	elif command == SectorOrEnocde.enodeb and choice == GetSectorEnocdeChoice.id:
# 		command = "SELECT ENODEB_ID From tbCell GROUP BY ENODEB_ID"
# 	else:
# 		raise
# 	async with aiosqlite.connect("./data.db") as db:
# 		db.row_factory = aiosqlite.Row
# 		async with db.execute(command) as cursor:
# 			rows = await cursor.fetchall()
# 			if rows:
# 				return [row for row in rows]
# 			else:
# 				return []

"""
enode和sector的数据查询
"""


class TbcellModel(BaseModel):
    city: str
    sector_id: str
    sector_name: str
    enodebid: str
    enodeb_name: str
    earfcn: int
    pci: int
    pss: Optional[str]
    sss: Optional[str]
    tac: int
    vendor: str
    longitude: float
    latitude: float
    style: str
    azimuth: float
    height: float
    electtilt: float
    mechtilt: float
    totletilt: float

    class Config:
        def alias_generator(x): return x.upper()


@data_router.get("/sector/detail")
async def get_sector_detail(name_or_id: str, choice: GetSectorEnocdeChoice):
    """
    输入(或下拉列表)小区id或名称，返回sector全部信息
    """
    if choice == GetSectorEnocdeChoice.name:
        command = 'SELECT * From "tbCell" WHERE "SECTOR_NAME" = $1;'
    elif choice == GetSectorEnocdeChoice.id:
        command = 'SELECT * From "tbCell" WHERE "SECTOR_ID" = $1;'
    return await fetch_one_then_wrap_model(command, TbcellModel, name_or_id)


@data_router.get("/enodeb/detail")
async def get_enodeb_detail(name_or_id: str, choice: GetSectorEnocdeChoice):
    if choice == GetSectorEnocdeChoice.name:
        command = 'SELECT * From "tbCell" WHERE "ENODEB_NAME" = $1;'
    elif choice == GetSectorEnocdeChoice.id:
        command = 'SELECT * From "tbCell" WHERE "ENODEB_ID" = $1;'
    return await fetch_one_then_wrap_model(command, TbcellModel, name_or_id)


class KPIChoice(str, Enum):
    RCCConnSUCC = "RCCConnSUCC"
    RCCConnATT = "RCCConnATT"
    RCCConnRATE = "RCCConnRATE"


@data_router.get("/kpi/detail")
async def get_kpi_detail(name: str, choice: KPIChoice, start_time: datetime.date, end_time: datetime.date):
    command = 'SELECT "StartTime","{}" From "tbKPI" WHERE "ENODEB_NAME" = $1 AND "StartTime" BETWEEN $2 AND $3;'.format(
        choice.value)
    return await fetch_all(command, name, start_time, end_time)


class GranularityChoice(str, Enum):
    a15min = "15min"
    hour = "hour"


@data_router.get("/prb/detail")
async def get_avg_prb_line_chart(enodeb_name: str, granularity: GranularityChoice, prbindex: int, start_time: datetime.datetime, end_time: datetime.datetime):
    """
    输入网元，选择第i个PRB，选择时间区间和粒度，返回干扰噪声平均值折线图
    granularity : 粒度
    prbindex: 第几个prb
    enodeb_name: 网元名称
    """
    if granularity == GranularityChoice.a15min:
        command = f"""
        SELECT "StartTime","AvgNoise{prbindex}" 
        FROM  "tbPRB"
        WHERE "ENODEB_NAME" = $1 AND "StartTime" BETWEEN $2 AND $3
        """
        return await fetch_all(command, enodeb_name, start_time, end_time)

    else:
        connection = await get_connection()
        await connection.execute("CALL update_tbprb_new();")
        command = f"""
        SELECT "StartTime","AvgNoise{prbindex}" 
        FROM  "tbPRB"
        WHERE "ENODEB_NAME" = $1 AND "StartTime" BETWEEN $2 AND $3
        """
        result = await fetch_all(command, enodeb_name, start_time, end_time, connection=connection)
        await connection.close()
        return result


async def get_tbCell_pos():
    command = """
        select "SECTOR_ID","LONGITUDE","LATITUDE" from "tbCell";
    """
    pbCelldata = await fetch_all(command)
    ret = dict()
    for row in pbCelldata:
        ret[row["SECTOR_ID"]] = (row["LONGITUDE"], row["LATITUDE"])
    return ret


@data_router.get("/diagram")
async def network_interference_structure_diagram():
    """
    返回网络干扰结构图
    q 表示模块度
    """
    command = """
        SELECT "SCELL","NCELL","C2I_Mean"
        FROM  "tbC2I";
        """
    results = await fetch_all(command)
    pos = await get_tbCell_pos()
    nodes = {}
    edges = []
    for line in results:
        n1 = line["SCELL"]
        n2 = line["NCELL"]
        nodes[n1] = 1
        nodes[n2] = 1
        w = float(line["C2I_Mean"])
        edges.append(((n1, n2), w))
    nodes_, edges_ = in_order(nodes, edges)
    pyl = PyLouvain(nodes_, edges_)
    # node_dict = pyl.node_dict
    # reverse_node_dict = dict(zip(node_dict.values(), node_dict.keys()))
    partition, q = pyl.apply_method()
    # print(partition)
    print("模块度：", q)
    return {
        "nodes": [{"id": index, "lng": pos[node][0], "lat":pos[node][1]} for index, node in enumerate(nodes)],
        "partition": partition,
        "q": q,
    }
