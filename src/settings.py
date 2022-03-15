from enum import Enum


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
