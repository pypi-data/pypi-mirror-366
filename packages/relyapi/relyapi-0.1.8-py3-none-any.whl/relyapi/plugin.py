from abc import abstractmethod
from enum import Enum
from typing import Dict, Any

from pydantic import BaseModel, Field


class RequestModel(BaseModel):
    url: str
    method: str
    headers: Dict[str, str] = Field(default_factory=dict)
    body: Dict[str, Any] = Field(default_factory=dict, alias="json")

    class Config:
        populate_by_name = True


class BypassType(Enum):
    RAW = "RAW"
    TLS = "TLS"


class BasePlugin:
    domain: str

    # 请求配置
    use_proxy: bool = False  # 是否使用代理
    bypass_type: BypassType = BypassType.RAW  # 使用什么请求类型

    # 运行配置
    use_process: bool = False  # 是否使用进程模式执行
    timeout = 5

    @abstractmethod
    def invoke(self, url, method, headers: Dict[str, str], body: Dict[str, Any]) -> RequestModel:
        raise NotImplementedError("Subclasses must implement this method")
