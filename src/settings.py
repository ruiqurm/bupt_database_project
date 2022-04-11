import datetime
from enum import Enum
import re
import json
import platform
from statistics import mode

from src import model


class Settings:
    """
    Databse
    """
    DATABASE_USER = "postgres"
    DATABASE_PASSWORD = None
    DEFAULT_DATABASE = "tb"

    """
	User Rule
	"""
    USERNAME_MAX_LENGTH = 32
    USERNAME_MIN_LENGTH = 4
    PASSWORD_MAX_LENGTH = 16
    PASSWORD_MIN_LENGTH = 8
    USERNAME_RULE = re.compile("^[a-zA-Z\d\!@#$%\^&\*\(\)~`,.;'\x20]*$")
    PASSWORD_RULE = re.compile("^[a-zA-Z\d\!@#$%\^&\*\(\)~`,.;'\x20]*$")

    """
	User Token
	"""
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 720  # 12小时
    PAYLOAD_NAME = "bupt"

    """
	Router
	"""
    DATA_ROUTER_PREFIX = "/data"

    MAX_ROW_PER_FILE = 50000
    TEMPDIR = "/.tb"


class ValidUploadTableName(str, Enum):
    tbCell = "tbcell"
    tbKPI = "tbkpi"
    tbPRB = "tbprb"
    tbMROData = "tbmordata"
    tbC2I = "tbc2i"


class ValidTableName(str, Enum):
    tbCell = "tbcell"
    tbKPI = "tbkpi"
    tbPRB = "tbprb"
    tbMROData = "tbmordata"
    tbPRBnew = "tbprb"
    tbC2I = "tbc2i"


str2Model = {
    key:value for key,value in vars(model).items() if key.startswith("tb")
}

# __column_count = {
#     "tbCell": 19,
#     "tbPRB": 104,
#     "tbKPI": 7,
#     "tbMROData": 7,
#     "tbC2I": 8
# }

# __type_change = {
#     "tbCell": {
#         "int": (3, 5, 6, 9),
#         "float": (11, 12, 14, 15, 16, 17, 18),
#         "none": (7, 8)
#     },
#     "tbKPI": {
#         "int": (4, 5),
#         "float": (6,),
#         "date": ((0, "%m/%d/%Y %H:%M:%S"),),
#     },
#     "tbPRB": {
#         "date": ((0, "%m/%d/%Y %H:%M:%S"),),
#         "int": range(4, 104),
#     },
#     "tbC2I": {
#         "float": range(3, 8)
#     },
# }


# def get_insert_command(table_name: ValidUploadTableName):
#     return "INSERT INTO \"{}\" VALUES ({});".format(table_name.name, ",".join([f"${i}" for i in range(1, __column_count[table_name.name]+1)]))


# def transform_type(table_name: ValidUploadTableName, row: list) -> list:
#     change = __type_change[table_name.name]
#     if "int" in change:
#         for i in change["int"]:
#             try:
#                 row[i] = int(row[i])
#             except:
#                 row[i] = None
#     if "float" in change:
#         for i in change["float"]:
#             try:
#                 row[i] = float(row[i])
#             except:
#                 row[i] = None
#     if "none" in change:
#         for i in change["none"]:
#             row[i] = None
#     if "date" in change:
#         for i, pattern in change["date"]:
#             row[i] = datetime.datetime.strptime(row[i], pattern)
#     return row


try:
    _config = json.load(open("config.json"))
except FileNotFoundError:
    print("缺少数据库配置文件，默认按照user=postgres连接")
    Settings.DATABASE_USER = "postgres"
    Settings.DATABASE_PASSWORD = None
else:
    Settings.DATABASE_USER = _config.get("username", "postgres")
    Settings.DATABASE_PASSWORD = _config.get("password", None)


if(platform.system() == 'Windows'):
    import os
    Settings.TEMPDIR = "{}{}".format(os.getcwd(), Settings.TEMPDIR)
else:
    Settings.TEMPDIR = "{}{}".format("/tmp", Settings.TEMPDIR)
