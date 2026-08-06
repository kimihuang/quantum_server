"""自定义异常 - 统一错误码，方便前端处理。"""

from typing import Any


class AppError(Exception):
    """应用基类异常。"""

    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 400, detail: Any = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class NotFoundError(AppError):
    """资源未找到。"""

    def __init__(self, resource: str = "", id_value: Any = None):
        msg = f"{resource} (id={id_value}) 不存在" if id_value else f"{resource} 不存在"
        super().__init__(message=msg, code="NOT_FOUND", status_code=404)


class BusinessError(AppError):
    """业务逻辑错误。"""

    def __init__(self, message: str, detail: Any = None):
        super().__init__(message=message, code="BUSINESS_ERROR", status_code=422, detail=detail)


class ValidationError(AppError):
    """参数校验错误。"""

    def __init__(self, message: str, detail: Any = None):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422, detail=detail)
