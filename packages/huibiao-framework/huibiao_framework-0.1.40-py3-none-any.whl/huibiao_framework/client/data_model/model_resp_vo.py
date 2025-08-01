from pydantic import BaseModel, Field, field_validator
from typing import Generic, TypeVar, Optional, List
from pydantic_core.core_schema import FieldValidationInfo

from huibiao_framework.execption.model import (
    HuiZeModelResponseCodeError,
    HuiZeModelResponseFormatError,
)

T = TypeVar("T")


class ModelBaseRespVo(BaseModel, Generic[T]):

    # 响应状态码，0通常表示成功
    code: int = Field(..., description="响应状态码，0表示成功")

    # 响应消息
    message: str = Field("", description="响应状态描述信息")

    # 分析结果数据（泛型类型，可动态指定）
    result: Optional[T] = Field(None, description="分析结果数据，类型由泛型参数指定")

    @field_validator("code")
    def check_code_valid(cls, v: int) -> int:
        if v is None or v != 0:
            # 校验 code 合法性（通常 0 表示成功，非 0 表示错误）
            raise  HuiZeModelResponseCodeError(v)
        return v

    @field_validator("result")
    def check_result_consistent_with_code(
        cls, v: Optional[T], info: FieldValidationInfo
    ) -> Optional[T]:
        code = info.data.get("code")
        if code == 0 and v is None:
            # 整体后处理校验：code=0 时 result 必存在
            raise HuiZeModelResponseFormatError("Field 'result' is empty!")
        return v