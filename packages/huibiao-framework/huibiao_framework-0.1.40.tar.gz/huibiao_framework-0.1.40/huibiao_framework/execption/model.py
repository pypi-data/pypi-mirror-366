from typing import Optional

from huibiao_framework.execption.execption import HuiBiaoException


class HuiZeModelException(HuiBiaoException):
    pass


class HuiZeModelResponseFormatError(HuiZeModelException):
    def __init__(self, msg: str):
        super().__init__(f"模型返回结果错误，报错 {msg}")


class HuiZeModelResponseCodeError(HuiZeModelException):
    def __init__(self, code: Optional[int]):
        self.code = code
        super().__init__(f"模型处理失败，code={self.code}!")


class LLMException(HuiZeModelException):
    pass

class Qwen32bAwqException(LLMException):
    pass

class Qwen32bAwqResponseFormatError(Qwen32bAwqException):
    def __init__(self, msg: str):
        super().__init__(f"模型返回结果错误，报错 {msg}")
