"""
ORM 

从sql文件中提取得到
cat 1_create_table.sql|awk '/^"/{print $0}'|sed -e 's/,/\n/g' |sed -e 's/"//g'|sed -e 's/,//g'|sed -e 's/varchar([0-9]*)/str/g'|sed -e 's/date/datetime.date/g' |awk '{print $1":"$2}'| sed -e 's/:$//g' | sed -e s/\n\n/\n/g'
"""

import datetime
from tkinter import E
from typing import Optional
import pydantic

class getInsertCmdMixin():
	INSERT_METHOD = None
	@classmethod
	def get_insert_command(cls)->str:
		if cls.INSERT_METHOD is None:
			cls.INSERT_METHOD = "INSERT INTO {} VALUES ({});".format(cls.__name__, ",".join([f"${i}" for i in range(1, len(cls.__fields__)+1)]))
		return cls.INSERT_METHOD
	
	@classmethod
	def from_tuple(cls,tuple:tuple,ignore_but_log=False):
		if not ignore_but_log:
			return cls(**{key: tuple[i] for i, key in enumerate(cls.__fields__.keys())})
		else:
			try:
				return cls(**{key: tuple[i] for i, key in enumerate(cls.__fields__.keys())})
			except Exception:
				return None

	def to_tuple(self)->tuple:
		return [getattr(self, key) for key in self.__fields__.keys()]
class tbCell(pydantic.BaseModel,getInsertCmdMixin):
	CITY:str
	SECTOR_ID:str
	SECTOR_NAME:str
	ENODEBID:int
	ENODEB_NAME:str
	EARFCN:int
	PCI:int
	PSS:Optional[int]
	SSS:Optional[int]
	TAC:int
	VENDOR:str
	LONGITUDE:float
	LATITUDE:float
	STYLE:str
	AZIMUTH:float
	HEIGHT:Optional[float]
	ELECTTILT:Optional[float]
	MECHTILT:Optional[float]
	TOTLETILT:Optional[float]
	
	# ignore value 
	@pydantic.validator("PSS", pre=True)
	def parse_pss(cls, value):
		return None

	# ignore value 
	@pydantic.validator("SSS", pre=True)
	def parse_sss(cls, value):
		return None
	@pydantic.validator("HEIGHT", pre=True)
	def parse_1(cls, value):
		try:
			value = float(value)
		except Exception:
			return None
		return value
	@pydantic.validator("ELECTTILT", pre=True)
	def parse_2(cls, value):
		try:
			value = float(value)
		except Exception:
			return None
		return value
	@pydantic.validator("MECHTILT", pre=True)
	def parse_3(cls, value):
		try:
			value = float(value)
		except Exception:
			return None
		return value
	@pydantic.validator("TOTLETILT", pre=True)
	def parse_4(cls, value):
		try:
			value = float(value)
		except Exception:
			return None
		return value
class tbMROData(pydantic.BaseModel,getInsertCmdMixin):
	TimeStamp:str
	ServingSector:str
	InterferingSector:str
	LteScRSRP:str
	LteNcRSRP:str
	LteNcEarfcn:str
	LteNcPci:str

class tbKPI(pydantic.BaseModel,getInsertCmdMixin):
	StartTime:datetime.date
	ENODEB_NAME:str
	SECTOR_DESCRIPTION:str
	SECTOR_NAME:str
	RCCConnSUCC:int
	RCCConnATT:int
	RCCConnRATE:float
	__DATETIME_PATTERN = "%m/%d/%Y %H:%M:%S"
	@pydantic.validator("StartTime", pre=True)
	def parse_datetime(cls, value):
		return datetime.datetime.strptime(value, cls.__DATETIME_PATTERN)
class tbPRB(pydantic.BaseModel,getInsertCmdMixin):
	StartTime:datetime.date
	ENODEB_NAME:str
	SECTOR_DESCRIPTION:str
	SECTOR_NAME:str
	AvgNoise0:float
	AvgNoise1:float
	AvgNoise2:float
	AvgNoise3:float
	AvgNoise4:float
	AvgNoise5:float
	AvgNoise6:float
	AvgNoise7:float
	AvgNoise8:float
	AvgNoise9:float
	AvgNoise10:float
	AvgNoise11:float
	AvgNoise12:float
	AvgNoise13:float
	AvgNoise14:float
	AvgNoise15:float
	AvgNoise16:float
	AvgNoise17:float
	AvgNoise18:float
	AvgNoise19:float
	AvgNoise20:float
	AvgNoise21:float
	AvgNoise22:float
	AvgNoise23:float
	AvgNoise24:float
	AvgNoise25:float
	AvgNoise26:float
	AvgNoise27:float
	AvgNoise28:float
	AvgNoise29:float
	AvgNoise30:float
	AvgNoise31:float
	AvgNoise32:float
	AvgNoise33:float
	AvgNoise34:float
	AvgNoise35:float
	AvgNoise36:float
	AvgNoise37:float
	AvgNoise38:float
	AvgNoise39:float
	AvgNoise40:float
	AvgNoise41:float
	AvgNoise42:float
	AvgNoise43:float
	AvgNoise44:float
	AvgNoise45:float
	AvgNoise46:float
	AvgNoise47:float
	AvgNoise48:float
	AvgNoise49:float
	AvgNoise50:float
	AvgNoise51:float
	AvgNoise52:float
	AvgNoise53:float
	AvgNoise54:float
	AvgNoise55:float
	AvgNoise56:float
	AvgNoise57:float
	AvgNoise58:float
	AvgNoise59:float
	AvgNoise60:float
	AvgNoise61:float
	AvgNoise62:float
	AvgNoise63:float
	AvgNoise64:float
	AvgNoise65:float
	AvgNoise66:float
	AvgNoise67:float
	AvgNoise68:float
	AvgNoise69:float
	AvgNoise70:float
	AvgNoise71:float
	AvgNoise72:float
	AvgNoise73:float
	AvgNoise74:float
	AvgNoise75:float
	AvgNoise76:float
	AvgNoise77:float
	AvgNoise78:float
	AvgNoise79:float
	AvgNoise80:float
	AvgNoise81:float
	AvgNoise82:float
	AvgNoise83:float
	AvgNoise84:float
	AvgNoise85:float
	AvgNoise86:float
	AvgNoise87:float
	AvgNoise88:float
	AvgNoise89:float
	AvgNoise90:float
	AvgNoise91:float
	AvgNoise92:float
	AvgNoise93:float
	AvgNoise94:float
	AvgNoise95:float
	AvgNoise96:float
	AvgNoise97:float
	AvgNoise98:float
	AvgNoise99:float
	__DATETIME_PATTERN = "%m/%d/%Y %H:%M:%S"
	@pydantic.validator("StartTime", pre=True)
	def parse_datetime(cls, value):
		return datetime.datetime.strptime(value, cls.__DATETIME_PATTERN)
class tbC2I(pydantic.BaseModel,getInsertCmdMixin):
	CITY:str
	SCELL:str
	NCELL:str
	PrC2I9:float
	C2I_Mean:float
	std:float
	sampleCount:float
	WeightedC2I:float

class tbMRODataExternal(pydantic.BaseModel,getInsertCmdMixin):
	TimeStamp:str
	ServingSector:str
	InterferingSector:str
	LteScRSRP:float
	LteNcRSRP:float
	LteNcEarfcn:int
	LteNcPci:int