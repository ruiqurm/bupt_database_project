from fastapi import status,HTTPException
from typing import Any,Optional,Dict
from starlette.exceptions import HTTPException as StarletteHTTPException
# from .main import app

class BaseException(HTTPException):
    """
    异常基类
    """
    def __init__(
        self,
        status_code:int=status.HTTP_400_BAD_REQUEST,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code,detail=detail,headers=headers)
        self.error_code = 0



class Unauthorization(BaseException):
    """
    未登录
    """
    def __init__(
        self,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误",headers={"WWW-Authenticate": "Bearer"})
class ValidateError(BaseException):
    def __init__(
        self,
        detail: Any = None,
    ) -> None:
        super().__init__(detail="账号或密码格式错误")
class InactiveUser(BaseException):
    def __init__(
        self,
    ) -> None:
        super().__init__(detail="用户未激活")
class CreateFailed(BaseException):
    def __init__(
        self,
    ) -> None:
        super().__init__(detail="创建失败")
class NoSuchUser(BaseException):
    def __init__(
        self,
    ) -> None:
        super().__init__(detail="没有这个用户")
class PermissionDenied(BaseException):
    def __init__(
        self,
    ) -> None:
        super().__init__(detail="权限不足")

class  UploadFailed(BaseException):
    def __init__(
        self,
        detail:str= "上传失败"
    ) -> None:
        super().__init__(detail=detail)