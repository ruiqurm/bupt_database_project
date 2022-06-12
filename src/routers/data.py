import asyncio
from distutils.log import fatal
from zipfile import ZipFile
from asyncore import read
import xml.etree.ElementTree as ET
import os
import zipfile
import sys
import pydantic

from src.model import tbC2I, tbCell, tbKPI, tbMROData
from ..pylouvain import PyLouvain, in_order
from fastapi.responses import FileResponse
from calendar import month
import uuid
from fastapi import BackgroundTasks
import fastapi
from ..utils import batch, fetch_all, fetch_one, fetch_one_then_wrap_model, get_connection,Logger
import datetime
from pydantic import BaseModel
import sqlite3
from fastapi import APIRouter, File, UploadFile
from enum import Enum
from ..settings import ValidTableName, ValidUploadTableName, str2Model, Settings
from typing import List, Optional, Dict, Union
from ..model import tbC2Inew, tbCell, tbMRODataExternal, tbPRB
import csv
import shutil
from scipy.stats import norm
import math 
from matplotlib import pyplot as plt 
import networkx as nx 
from io import BytesIO
from starlette.responses import StreamingResponse

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


async def upload_data_background(name: ValidUploadTableName, id: str, file, new_filepath: str, model: Union[tbCell, tbC2I, tbKPI, tbMROData,tbPRB], max_line: int):
    """后台上传

    Args:
        reader (csv.reader): _description_
        table_name (str): _description_
        command (str): _description_  
    """
    counter = 0
    connection = await get_connection()
    reader = csv.reader(file, delimiter=',', quotechar='"')
    next(reader)  # 跳过标题
    try:
        command = model.get_insert_command()
        async with connection.transaction():
            for fifty_rows in batch(iter(reader), max_line):
                list = []
                # 数据清洗：从要插入的记录中删除不满足约束条件的项
                for i in fifty_rows:
                    counter += 1
                    r = model.from_tuple(i)
                    if not r.constraints():
                        logger = Logger('datalog.txt')
                        logger.write(name+" insert error: "+"can not insert line "+str(counter)+"\n")
                    else:
                        list.append(r.to_tuple())

                await connection.executemany(command, list)
                __upload_dict[id].current_row = counter
    except Exception as e:
        __upload_dict[id].msg = str(e)
        __upload_dict[id].failed = True
    finally:
        __upload_dict[id].done = True
        file.close()
        os.remove(new_filepath)
    if isinstance(model,tbPRB):
        await connection.execute("CALL update_tbprb_new();")

@data_router.post("/upload")
async def upload_data(name: ValidUploadTableName, file: UploadFile, background_tasks: BackgroundTasks, encoding: str = "utf-8", max_line: int = 50):
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
    #将datalog中的内容清零
    with open("datalog.txt", 'r+') as f:
        f.truncate(0)

    id = uuid.uuid4().hex
    new_filepath = os.path.join(Settings.TEMPDIR, id)
    try:
        with open(new_filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()
    try:
        f = open(new_filepath, "r", encoding=encoding)
    except Exception:
        raise fastapi.HTTPException(status_code=400, detail="文件编码错误")

    __upload_dict[id] = UploadTask(id=id)
    background_tasks.add_task(upload_data_background,
                              name, id, f, new_filepath, str2Model[name.name], max_line)

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
        count = await connection.fetchrow(f'SELECT COUNT(*) FROM {table_name}')
        count = count["count"]
        max_row = Settings.MAX_ROW_PER_FILE
        for i in range(0, count, max_row):
            id = uuid.uuid4().hex + ".csv"
            command = f'COPY (select * from {table_name} LIMIT {max_row} OFFSET {i}) TO \'{Settings.TEMPDIR}/{id}\' WITH (FORMAT CSV, HEADER);'
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


"""
enode和sector的数据查询
"""


@data_router.get("/sector", response_model=List[Dict[str, str]])
async def get_sector_detail(choice: GetSectorEnocdeChoice):
    """
    获取全部小区id或者名称
    """
    if choice == GetSectorEnocdeChoice.name:
        command = 'SELECT "SECTOR_NAME" From tbCell;'
    elif choice == GetSectorEnocdeChoice.id:
        command = 'SELECT "SECTOR_ID" From tbCell;'
    return await fetch_all(command)


@data_router.get("/sector/detail", response_model=tbCell)
async def get_sector_detail(name_or_id: str, choice: GetSectorEnocdeChoice):
    """
    输入(或下拉列表)小区id或名称，返回sector全部信息
    """
    if choice == GetSectorEnocdeChoice.name:
        command = 'SELECT * From tbCell WHERE "SECTOR_NAME" = $1;'
    elif choice == GetSectorEnocdeChoice.id:
        command = 'SELECT * From tbCell WHERE "SECTOR_ID" = $1;'
    return await fetch_one_then_wrap_model(command, tbCell, name_or_id)


@data_router.get("/enodeb/detail", response_model=List[tbCell])
async def get_enodeb_detail(name_or_id: str, choice: GetSectorEnocdeChoice):
    if choice == GetSectorEnocdeChoice.name:
        command = 'SELECT * From tbCell WHERE "ENODEB_NAME" = $1;'
    elif choice == GetSectorEnocdeChoice.id:
        command = 'SELECT * From tbCell WHERE "ENODEBID" = $1;'
        name_or_id = int(name_or_id)
    return [tbCell(**i) for i in await fetch_all(command,name_or_id)]


@data_router.get("/enodeb", response_model=List[Dict[str, str]])
async def get_sector_detail(choice: GetSectorEnocdeChoice):
    """
    获取全部小enode id或者名称
    """
    if choice == GetSectorEnocdeChoice.name:
        command = 'SELECT "ENODEB_NAME" From tbCell;'
    elif choice == GetSectorEnocdeChoice.id:
        command = 'SELECT "ENODEBID" From tbCell;'
    return await fetch_all(command)


class KPIChoice(str, Enum):
    RCCConnSUCC = "RCCConnSUCC"
    RCCConnATT = "RCCConnATT"
    RCCConnRATE = "RCCConnRATE"


class kpi_detail(pydantic.BaseModel):
    StartTime: datetime.date
    Data: Union[int, float, str]


@data_router.get("/kpi/detail")
async def get_kpi_detail(name: str, choice: KPIChoice, start_time: datetime.date, end_time: datetime.date):
    # command = """
    # SELECT "StartTime","{}" as "Data" From tbKPI WHERE "ENODEB_NAME" = (select "ENODEB_NAME" from tbKPI where "SECTOR_NAME"='{}' limit 1) AND "StartTime" BETWEEN $1 AND $2;""".format(
    #     choice.value,name)
    command = """
    SELECT "StartTime","{}" as "Data" From tbKPI WHERE "SECTOR_NAME" = '{}' AND "StartTime" BETWEEN $1 AND $2;""".format(
        choice.value,name)
    return await fetch_all(command,start_time, end_time)


class GranularityChoice(str, Enum):
    a15min = "15min"
    hour = "hour"


class prb_detail(pydantic.BaseModel):
    StartTime: datetime.date
    AvgNoise: float


@data_router.get("/prb/detail")
async def get_avg_prb_line_chart(name: str, granularity: GranularityChoice, prbindex: int, start_time: datetime.datetime, end_time: datetime.datetime):
    """
    输入网元，选择第i个PRB，选择时间区间和粒度，返回干扰噪声平均值折线图
    granularity : 粒度
    prbindex: 第几个prb
    name: 小区名称
    """
    if granularity == GranularityChoice.a15min:
        # command = f"""
        # SELECT "StartTime","AvgNoise{prbindex}" as "AvgNoise"
        # FROM  tbPRB
        # WHERE "ENODEB_NAME" = (select "ENODEB_NAME" from tbKPI where "SECTOR_NAME"='{name}' limit 1) AND "StartTime" BETWEEN $1 AND $2
        # """
        command = f"""
        SELECT "StartTime","AvgNoise{prbindex}" as "AvgNoise"
        FROM  tbPRB
        WHERE "ENODEB_NAME" = '{name}' AND "StartTime" BETWEEN $1 AND $2
        """
        return await fetch_all(command, start_time, end_time)

    else:
        connection = await get_connection()
        # command = f"""
        # SELECT "StartTime","AvgNoise{prbindex}" as "AvgNoise"
        # FROM  tbPRB
        # WHERE "ENODEB_NAME" = (select "ENODEB_NAME" from tbKPI where "SECTOR_NAME"='{name}' limit 1) AND "StartTime" BETWEEN $2 AND $3
        # """
        command = f"""
        SELECT "StartTime","AvgNoise{prbindex}" as "AvgNoise"
        FROM  tbPRBnew
        WHERE "ENODEB_NAME" = '{name}' AND "StartTime" BETWEEN $1 AND $2
        """
        result = await fetch_all(command,start_time, end_time, connection=connection)
        await connection.close()
        return result


async def get_tbCell_pos():
    command = """
        select "SECTOR_ID","LONGITUDE","LATITUDE" from tbCell;
    """
    pbCelldata = await fetch_all(command)
    ret = dict()
    for row in pbCelldata:
        ret[row["SECTOR_ID"]] = (row["LONGITUDE"], row["LATITUDE"])
    return ret


class diagramResponseModel(pydantic.BaseModel):
    class Node(pydantic.BaseModel):
        id: str
        lng: str
        lat: str
    nodes: List[Node]
    partition: List[List[int]]
    q: float

from typing import Tuple
@data_router.get("/diagram", response_model=diagramResponseModel)
async def network_interference_structure_diagram(threshold:float,figure_width=20,figure_height=20):
    """
    返回网络干扰结构图
    q 表示模块度
    """
    command = """
        SELECT "SCELL","NCELL","C2I_Mean"
        FROM  tbC2I;
        """
    results = await fetch_all(command)
    pos = await get_tbCell_pos()
    results = [item for item in results if item["SCELL"] in pos and item["NCELL"] in pos]
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
    # nodes = [{"id": index, "lng": pos[node][0], "lat":pos[node][1]} for index, node in enumerate(nodes)]

    pyl = PyLouvain(nodes_, edges_)
    node_dict = {node:index for index, node in enumerate(nodes)}
    reverse_node_dict = dict(zip(node_dict.values(), node_dict.keys()))
    partition, q = pyl.apply_method()
    # print(partition)
    # print("模块度：", q)
    community_num = len(partition) 
    # print('community_num:',community_num) 
    color_board = ['red','green','blue','pink','orange','purple','scarlet'] 
    color = {} 
    for index in range(community_num): 
            # print("社区"+str(index+1)+":"+str(len(partition[index]))) 
            for node_id in partition[index]: 
                    color[node_id] = color_board[index] # color 为一个字典，key 为编号形式的节点，value 为所属社区的颜色 
    new_color_dict = sorted(color.items(), key=lambda d:d[0], reverse = False)#  将 color 字典按照 key 的大小排序，并返回一个 list 
    node_list = [reverse_node_dict[item[0]] for item in new_color_dict] #存储编号从小到大顺序对应的 253916-2 的形式的节点 
    color_list = [item[1] for item in new_color_dict]#存储 node_list 中对应的节点颜色 
    # print(node_list) 
    # print(color_list) 
    
    #构建 networkx 无向图 
    G = nx.Graph() 
    edge_list = [] #存储边列表 
    edge_width = [] #存储边列表对应的边粗细 
    edge_color = [] #存储边列表对应的边颜色 
    for line in results:
        n1 = line["SCELL"]
        n2 = line["NCELL"]
        v = line["C2I_Mean"]
        G.add_edge(n1,n2,weight=float(v)) 
        edge_list.append([n1,n2]) 
        if color[node_dict[n1]] == color[node_dict[n2]]:#如果边的两端颜色相同 
                edge_color.append(color[node_dict[n1]]) #则使用点的颜色作为边的颜色 
        else: 
                edge_color.append('c') #否则使用其他颜色 
        if float(v) > threshold: #阈值 
                edge_width.append(float(v)/100.0) 
        else: 
                edge_width.append(0.0) 
    
    #  可视化 
    plt.figure(figsize=(figure_width,figure_height))
    _node = [int(item.split("-")[-1])%4 for item in node_list] #提取后缀模 4 取余 
    node_0_index_list,node_1_index_list,node_2_index_list,node_3_index_list = [], [], [], [] 
    for index,item in enumerate(_node): #划分不同后缀余数的群，以便给每个群分配一个节点的形状  node_shape  防止都用圆形，导致同一经纬度的节点重叠在一起 
        if item == 0: 
                node_0_index_list.append(index) 
        if item == 1: 
                node_1_index_list.append(index) 
        if item == 2: 
                node_2_index_list.append(index) 
        if item == 3: 
                node_3_index_list.append(index) 
    print("node_list:",_node) 
    nx.draw_networkx_nodes(G,  pos,  nodelist=[node_list[i]  for  i  in 
    node_0_index_list],node_shape=7,  node_color=[color_list[i]  for  i  in  node_0_index_list], 
    node_size=50) 
    nx.draw_networkx_nodes(G,  pos,  nodelist=[node_list[i]  for  i  in 
    node_1_index_list],node_shape=4,  node_color=[color_list[i]  for  i  in  node_1_index_list], 
    node_size=50) 
    nx.draw_networkx_nodes(G,  pos,  nodelist=[node_list[i]  for  i  in 
    node_2_index_list],node_shape=5,  node_color=[color_list[i]  for  i  in  node_2_index_list], 
    node_size=50) 
    nx.draw_networkx_nodes(G,  pos,  nodelist=[node_list[i]  for  i  in 
    node_3_index_list],node_shape=6,  node_color=[color_list[i]  for  i  in  node_3_index_list], 
    node_size=50) 
    nx.draw_networkx_edges(G,  pos,  edgelist  =  edge_list,  width  =  edge_width,  alpha=1, edge_color=edge_color) 
    buf = BytesIO()
    plt.savefig(buf,format="jpeg")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/jpeg")

def support_gbk(zip_file: ZipFile):
    # ref:https://blog.csdn.net/qq_21076851/article/details/122752196
    name_to_info = zip_file.NameToInfo
    # copy map first
    for name, info in name_to_info.copy().items():
        real_name = name.encode('cp437').decode('gbk')
        if real_name != name:
            info.filename = real_name
            del name_to_info[name]
            name_to_info[real_name] = info
    return zip_file

async def async_parse_mro(f:str,pci2id,encoding="utf-8"):
    # result = []
    connection = await get_connection()
    command = tbMRODataExternal.get_insert_command()
    with open(f, "r",encoding=encoding) as file:
        tree = ET.parse(file)
        root = tree.getroot()
        assert len(root) == 2, "文件不符合要求"
        # header = root[0]
        smr = root[1][0][0]
        FIELD = ("MR.LteScRSRP", "MR.LteNcRSRP", "MR.LteScEarfcn", "MR.LteNcPci")
        smr = smr.text.split()
        index = [smr.index(i) for i in FIELD]
        
        result = []
        for data in root[1][0][1:]:
            timeStamp = data.attrib["TimeStamp"]
            for object in data:
                object = object.text.split()
                try:
                    scid = pci2id[int(object[5])]
                    ncid = pci2id[int(object[7])]
                except ValueError:
                    continue
                d =tbMRODataExternal.from_tuple((timeStamp, scid,ncid, object[index[0]], object[index[1]], object[index[2]], object[index[3]]),ignore_but_log=True)
                if d is not None:
                    result.append(d.to_tuple())
        try:    
            await connection.executemany(command,result)
        except Exception as e:
            print(e)
    print("Done")


@data_router.post("/mro_parse")
async def mro(file: UploadFile,encoding:str="utf-8"):
    zipfilename = uuid.uuid4().hex
    filename = "".join(file.filename.split(".")[:-1])
    zipfilepath = os.path.join(Settings.TEMPDIR,zipfilename)
    try:
        with open(zipfilepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()
    folder_path = os.path.join(Settings.TEMPDIR,uuid.uuid4().hex)
    os.mkdir(folder_path)
    try:
        with support_gbk(ZipFile(zipfilepath)) as zfp:
            zfp.extractall(folder_path)        
    finally:
        os.remove(zipfilepath)

    connection = await get_connection()
    pci2id = {i["PCI"]:i["SECTOR_ID"] for i in await fetch_all('SELECT "SECTOR_ID","PCI" From tbCell;',connection=connection)}
    connection.close()
    try:
        unzip_path = os.path.join(folder_path, filename)
        files = []
        for r, d, f in os.walk(unzip_path):
            for file in f:
                if file.endswith(".xml") and file.startswith("TD-LTE_MRO_"):
                    files.append(os.path.join(r, file))
        await asyncio.gather(*[async_parse_mro(f,pci2id,encoding) for f in files])
    except Exception as e:
        return f"failed when unzipping {str(e)}"
    finally:
        shutil.rmtree(folder_path)
    return "ok"
# async def upload_mro(file,encoding):
#     counter = 0
#     connection = await get_connection()
#     reader = csv.reader(file, delimiter=',', quotechar='"')
#     next(reader)  # 跳过标题
#     try:
#         command = model.get_insert_command()
#         async with connection.transaction():
#             for fifty_rows in batch(iter(reader), max_line):
#                 # 没做触发器
#                 counter += max_line
#                 await connection.executemany(command, [model.from_tuple(i).to_tuple() for i in fifty_rows])
#                 __upload_dict[id].current_row = counter
#     except Exception as e:
#         __upload_dict[id].msg = str(e)
#         __upload_dict[id].failed = True
#     finally:
#         __upload_dict[id].done = True
#         file.close()
#         os.remove(new_filepath)
"""
tbC2I干扰分析
"""

@data_router.post("/generate_tbC2Inew")
async def generate_tbC2Inew(n: int):
    command = f"""
    with tmp as (
	select "ServingSector" as "SCELL", "InterferingSector" as "NCELL", ("LteScRSRP"-"LteNcRSRP") as "C2I"
    from tbMROData
    where ("ServingSector", "InterferingSector") in (select "ServingSector", "InterferingSector"
				                                     from tbMROData
				                                     group by "ServingSector", "InterferingSector"
				                                     having count(*)>=$1) )
    select "SCELL", "NCELL", avg("C2I") as "C2I_Mean", stddev("C2I") as "std"
    from tmp
    group by "SCELL", "NCELL";
    """
    data = await fetch_all(command,n)
    id = uuid.uuid4().hex
    __upload_dict[id] = UploadTask(id=id)
    connection = await get_connection()
    try:
        command1 = tbC2Inew.get_insert_command()
        await connection.execute("DELETE FROM tbC2Inew;")
        for i in data:
            t1 = tuple(i)
            t2 = (norm.cdf(9,t1[2],t1[3]), norm.cdf(6,t1[2],t1[3])-norm.cdf(-6,t1[2],t1[3]))
            t3 = t1+t2
            await connection.executemany(command1, [tbC2Inew.from_tuple(t3).to_tuple()])

    except Exception as e:
        __upload_dict[id].msg = str(e)
        __upload_dict[id].failed = True
    finally:
        __upload_dict[id].done = True

    return {"id": id, "url": f"{Settings.DATA_ROUTER_PREFIX}/upload/status?id={id}"}

"""
重叠覆盖干扰小区三元组分析
"""

@data_router.post("/generate_tbC2I3")
async def generate_tbC2I3(x: int):
    command = f"""
    select "SCELL", "NCELL"
    from tbC2Inew
    where "PrbABS6">=($1/100);
    """
    data = await fetch_all(command,x)
    listName = [] #存放data中小区ID的列表
    res = [] #存放结果的列表

    for i in data:
        t = tuple(i)
        if t[0] not in listName:
            listName.append(t[0])
        
        if t[1] not in listName:
            listName.append(t[1])

    for i in data:
        t = tuple(i)
        for id in listName:
            if id != t[0] and id != t[1] :
                if ((id, t[0]) in data or (t[0], id) in data) and ((id, t[1]) in data or (t[1], id) in data):
                    list = []
                    list.append(id)
                    list.append(t[0])
                    list.append(t[1])
                    list.sort()
                    tmp = tuple(list)
                    if tmp not in res:
                        res.append(tmp)
                    
    model = str2Model["tbc2i3"]
    id = uuid.uuid4().hex
    __upload_dict[id] = UploadTask(id=id)
    connection = await get_connection()
    try:
        command1 = model.get_insert_command()
        await connection.execute("DELETE FROM tbC2Inew;")
        for i in res:
            await connection.executemany(command1, [model.from_tuple(i).to_tuple()])

    except Exception as e:
        __upload_dict[id].msg = str(e)
        __upload_dict[id].failed = True
    finally:
        __upload_dict[id].done = True

    return {"id": id, "url": f"{Settings.DATA_ROUTER_PREFIX}/upload/status?id={id}"}
