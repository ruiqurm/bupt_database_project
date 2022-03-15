import datetime
from pydantic import BaseModel
import sqlite3
from fastapi import APIRouter, File, UploadFile
import aiosqlite
import aiofiles
from enum import Enum
from ..exceptions import UploadFailed
from ..settings import ValidTableName, get_insert_command
import csv

data_router = APIRouter(
    prefix="/data",
    tags=["data"],
)


@data_router.post("/upload/{table}")
async def upload_data(table: ValidTableName, file: UploadFile, encoding: str = "utf-8"):
    if table == ValidTableName.tbcell or table == ValidTableName.tbkpi or \
            table == ValidTableName.tbprb or table == ValidTableName.tbmordata:
        contents = await file.read()
        data = contents.decode(encoding).splitlines()
        reader = csv.reader(data, delimiter=',', quotechar='"')
        command = get_insert_command(table)

        async with aiosqlite.connect("./data.db") as db:
            await db.execute("BEGIN")  # 开始事务
            next(reader)
            try:
                for count, row in enumerate(reader):
                    await db.execute(command, row)
                await db.execute("COMMIT")
                await db.commit()
            except sqlite3.ProgrammingError as e:
                raise UploadFailed("{}行: {}".format(count, str(e)))
            except sqlite3.Error as e:
                raise UploadFailed(str(e))
            return "ok"
    else:
        raise


class GetSectorEnocdeChoice(str, Enum):
    name = "name"
    id = "id"


class SectorOrEnocde(str, Enum):
    sector = "sector"
    enodeb = "enodeb"

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
    pss: str
    sss: str
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


@data_router.get("/{category}/detail")
async def get_sector_detail(category: SectorOrEnocde, name_or_id: str, choice: GetSectorEnocdeChoice):
    """
    输入(或下拉列表)小区id或名称，返回sector全部信息
    """
    if category == SectorOrEnocde.sector and choice == GetSectorEnocdeChoice.name:
        command = "SELECT * From tbCell WHERE SECTOR_NAME = ?"
    elif category == SectorOrEnocde.sector and choice == GetSectorEnocdeChoice.id:
        command = "SELECT * From tbCell WHERE SECTOR_ID = ?"
    elif category == SectorOrEnocde.enodeb and choice == GetSectorEnocdeChoice.name:
        command = "SELECT * From tbCell WHERE ENODEB_NAME = ?"
    elif command == SectorOrEnocde.enodeb and choice == GetSectorEnocdeChoice.id:
        command = "SELECT * From tbCell WHERE ENODEB_ID = ?"
    else:
        raise
    async with aiosqlite.connect("./data.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(command, (name_or_id,)) as cursor:
            rows = await cursor.fetchone()
            if rows:
                return TbcellModel(**rows).dict()
            else:
                return {}


class GranularityChoice(Enum, str):
    a15min = "15min"
    a30min = "30min"
    hour = "hour"


@data_router.get("/prb")
def get_avg_prb_line_chart(enodeb_name: str, prbindex: int, granularity: GranularityChoice, from_time: datetime.datetime, to_time: datetime.datetime):
    """
    输入网元，选择第i个PRB，选择时间区间和粒度，返回干扰噪声平均值折线图
    granularity : 粒度
    prbindex: 第几个prb
    enodeb_name: 网元名称
    """

    command = """
    SELECT StartTime,avg({}) from tbPRB where ENODEB_NAME = "{}"
    GROUP BY strftime("%s",substr(StartTime,7,4)||"-"|| substr(StartTime,1,2)||"-"|| substr(StartTime,4,2) ||  substr(StartTime,11,9)) / {};
    """
    pass


db = sqlite3.connect("data.db")
db.cursor().execute("""
create table IF NOT EXISTS tbCell ( 
"CITY" varchar(255),
"SECTOR_ID" varchar(50), 
"SECTOR_NAME" varchar(255), 
"ENODEBID" int, 
"ENODEB_NAME" varchar(255), 
"EARFCN" int, 
"PCI" int, 
"PSS" int, 
"SSS" int, 
"TAC" int, 
"VENDOR" varchar(255), 
"LONGITUDE" float, 
"LATITUDE" float, 
"STYLE" varchar(255), 
"AZIMUTH" float, 
"HEIGHT" float, 
"ELECTTILT" float, 
"MECHTILT" float, 
"TOTLETILT" float 
); 
""")
db.cursor().execute("""
create table IF NOT EXISTS tbPRB
(
"StartTime"  datetime,
"ENODEB_NAME"  varchar(255),
"SECTOR_DESCRIPTION"  varchar(255) not null,
"SECTOR_NAME"  varchar(255),
avg_noise0 float,avg_noise1 float,avg_noise2 float,avg_noise3 float,avg_noise4 float,avg_noise5 float,avg_noise6 float,avg_noise7 float,avg_noise8 float,avg_noise9 float,avg_noise10 float,avg_noise11 float,avg_noise12 float,avg_noise13 float,avg_noise14 float,avg_noise15 float,avg_noise16 float,avg_noise17 float,avg_noise18 float,avg_noise19 float,avg_noise20 float,avg_noise21 float,avg_noise22 float,avg_noise23 float,avg_noise24 float,avg_noise25 float,avg_noise26 float,avg_noise27 float,avg_noise28 float,avg_noise29 float,avg_noise30 float,avg_noise31 float,avg_noise32 float,avg_noise33 float,avg_noise34 float,avg_noise35 float,avg_noise36 float,avg_noise37 float,avg_noise38 float,avg_noise39 float,avg_noise40 float,avg_noise41 float,avg_noise42 float,avg_noise43 float,avg_noise44 float,avg_noise45 float,avg_noise46 float,avg_noise47 float,avg_noise48 float,avg_noise49 float,avg_noise50 float,avg_noise51 float,avg_noise52 float,avg_noise53 float,avg_noise54 float,avg_noise55 float,avg_noise56 float,avg_noise57 float,avg_noise58 float,avg_noise59 float,avg_noise60 float,avg_noise61 float,avg_noise62 float,avg_noise63 float,avg_noise64 float,avg_noise65 float,avg_noise66 float,avg_noise67 float,avg_noise68 float,avg_noise69 float,avg_noise70 float,avg_noise71 float,avg_noise72 float,avg_noise73 float,avg_noise74 float,avg_noise75 float,avg_noise76 float,avg_noise77 float,avg_noise78 float,avg_noise79 float,avg_noise80 float,avg_noise81 float,avg_noise82 float,avg_noise83 float,avg_noise84 float,avg_noise85 float,avg_noise86 float,avg_noise87 float,avg_noise88 float,avg_noise89 float,avg_noise90 float,avg_noise91 float,avg_noise92 float,avg_noise93 float,avg_noise94 float,avg_noise95 float,avg_noise96 float,avg_noise97 float,avg_noise98 float,avg_noise99 float
);
""")
db.commit()
