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
        error_code = 1
    ) -> None:
        super().__init__(status_code=status_code,detail=detail,headers=headers)
        self.error_code = error_code



class Unauthorization(BaseException):
    """
    未登录
    """
    def __init__(
        self,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="验证失败",headers={"WWW-Authenticate": "Bearer"},error_code=2)
class ValidateError(BaseException):
    def __init__(
        self,
        detail: Any = None,
    ) -> None:
        super().__init__(detail="账号或密码格式错误",error_code=3)
class InactiveUser(BaseException):
    def __init__(
        self,
    ) -> None:
        super().__init__(detail="用户未激活",error_code=4)
class OperationFailed(BaseException):
    """通用失败异常
    """
    def __init__(
        self,
        detail = "操作失败"
    ) -> None:
        super().__init__(detail=detail,error_code=5)
class NoSuchUser(BaseException):
    def __init__(
        self,
    ) -> None:
        super().__init__(detail="没有这个用户",error_code=6)
class PermissionDenied(BaseException):
    def __init__(
        self,
    ) -> None:
        super().__init__(detail="权限不足",error_code=7)
