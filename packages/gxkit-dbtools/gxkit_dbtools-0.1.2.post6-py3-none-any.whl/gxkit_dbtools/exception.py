"""
dbtools 事件层
Version 0.1.0
"""
from enum import IntEnum


class ErrorCode(IntEnum):
    GENERAL = 1000
    CONNECTION = 1001
    EXECUTION = 1002
    PARSE = 1003
    TOOLS = 1004


class DBToolsError(Exception):

    def __init__(self, message: str, *, code: int = ErrorCode.GENERAL):
        self.code = code
        self.message = message
        super().__init__(message)


class DBConnectionError(DBToolsError):
    def __init__(self, source: str, db_type: str, message: str = "Database connection error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[Database Type]: {db_type}\n"
            f"\t[Error Message]: {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=ErrorCode.CONNECTION)


class SQLExecutionError(DBToolsError):
    def __init__(self, source: str, sql: str, message: str = "SQL execute error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[SQL] : '{sql[:200]}{'...' if len(sql) >= 200 else ''}'\n"
            f"\t[Error Message] : {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=ErrorCode.EXECUTION)


class SQLParseError(DBToolsError):
    def __init__(self, source: str, sql: str, message: str = "SQL parse error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[SQL] : '{sql[:200]}{'...' if len(sql) >= 200 else ''}'\n"
            f"\t[Error Message] : {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=ErrorCode.PARSE)


class ToolError(DBToolsError):
    def __init__(self, source: str, message: str = "DB tools error"):
        full_message = (
            f"\n\t[Source] : {source}\n"
            f"\t[Error Message] : {message[:500]}{'...' if len(message) >= 500 else ''}"
        )
        super().__init__(full_message, code=ErrorCode.TOOLS)
