from enum import Enum
import re

class Settings:
	"""
	Databse
	"""
	DEFAULT_USER = "postgres"
	DEFAULT_PASSWORD = None
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
	ACCESS_TOKEN_EXPIRE_MINUTES = 720 # 12小时
	PAYLOAD_NAME = "bupt"

		

class ValidTableName(str,Enum):
	tbcell = "tbcell"
	tbkpi = "tbkpi"
	tbprb = "tbprb"
	tbmordata = "tbmordata"
__column_count ={
	"tbcell":19,
	"tbprb":104
}
def get_insert_command(table_name:ValidTableName):
	return "INSERT INTO {} VALUES ({})".format(table_name.value,",".join(["?"]*__column_count[table_name.value]))

