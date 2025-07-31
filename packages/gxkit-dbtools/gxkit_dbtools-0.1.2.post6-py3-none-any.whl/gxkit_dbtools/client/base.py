"""
dbtools.client 抽象层
Version 0.1.0
"""
from abc import ABC, abstractmethod
from typing import Sequence, Any


class BaseDBClient(ABC):
    """
    BaseDBClient - 数据库客户端抽象基类
    Version: 0.1.0
    所有数据库客户端都应继承该类并实现指定方法
    """

    @abstractmethod
    def connect(self, **kwargs):
        """连接数据库"""
        pass

    @abstractmethod
    def execute(self, sql: str, **kwargs) -> Any:
        """执行单条 SQL 语句"""
        pass

    @abstractmethod
    def close(self):
        """关闭数据库连接"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
