from pydantic import BaseModel
from typing import Any
class CommonResponse(BaseModel):
	code: int
	msg: str
	data: Any = None