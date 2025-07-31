import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Union, List

import pandas as pd
from iotdb.Session import Session
from iotdb.SessionPool import SessionPool, create_session_pool, PoolConfig

from gxkit_dbtools.client.base import BaseDBClient
from gxkit_dbtools.exception import DBConnectionError, SQLExecutionError
from gxkit_dbtools.parser.sql_parser import SQLParser

try:
    from iotdb.utils.exception import IoTDBConnectionException
except ImportError:
    try:
        from iotdb.utils.IoTDBConnectionException import IoTDBConnectionException
    except ImportError as e:
        raise ImportError(
            "[IoTDBClient] Failed to import IoTDBConnectionException. Please check apache-iotdb version"
        ) from e


class IoTDBBaseClient(BaseDBClient):
    """
    IoTDBBaseClient - IoTDB 客户端
    Version: 0.1.2
    """

    def __init__(self, reconnect_delay: int = 10, **connection_params):
        self.db_type = "iotdb"
        self._connection_params = connection_params
        self._last_success_time: Optional[datetime] = None
        self._reconnect_delay = timedelta(minutes=reconnect_delay)
        self.connect()

    def _get_session(self):
        raise NotImplementedError

    def _return_session(self, session) -> None:  # noqa: D401
        pass

    def _check_and_reconnect(self, session) -> None:
        raise NotImplementedError

    def _execute_core(self, session, sql: str, sql_type: str) -> Union[pd.DataFrame, int, None]:
        raise NotImplementedError

    def execute(self, sql: str, max_retry: int = 3,prefix_path:int=1) -> Union[pd.DataFrame, int, None]:
        parser = SQLParser(sql, db_type="iotdb")
        sql_type = parser.sql_type()
        for attempt in range(1, max_retry + 1):
            session = self._get_session()
            try:
                self._check_and_reconnect(session)
                result = self._execute_core(session, parser.sql(), sql_type)
                if result is not None:
                    result.columns = self._build_col_mapping(list(result.columns), prefix_path)
                self._last_success_time = datetime.now()
                return result
            except (IoTDBConnectionException, BrokenPipeError, ConnectionError) as e:
                logging.warning(
                    f"[IoTDBBaseClient] Retry {attempt}/{max_retry} on {sql_type} | {e}"
                )
                self.close()
                self.connect()
                time.sleep(0.5)
            except Exception as e:
                raise SQLExecutionError("IoTDBBaseClient.execute", sql, str(e)) from e
            finally:
                self._return_session(session)
        raise SQLExecutionError("IoTDBBaseClient.execute", sql, f"Failed after {max_retry} retries")

    @staticmethod
    def _build_col_mapping(raw_cols: List[str], prefix_path: int) -> List[str]:
        def shorten(col: str) -> str:
            if col.lower() == "time":
                return "timestamp"
            if "(" in col and ")" in col:
                start = col.index("(")
                end = col.rindex(")")
                inner = col[start + 1: end]
                if "." in inner:
                    inner_short = ".".join(inner.split(".")[-prefix_path:]) if prefix_path > 0 else inner
                    return f"{col[: start + 1]}{inner_short}{col[end:]}"
                return col
            parts = col.split(".")
            return ".".join(parts[-prefix_path:]) if prefix_path > 0 else col

        return [shorten(col) for col in raw_cols]


class IoTDBClient(IoTDBBaseClient):
    """
    IoTDBClient - IoTDB 基础客户端
    Version: 0.1.2
    """

    def __init__(self, host: str, port: int, user: str, password: str, reconnect_delay: int = 10, **kwargs):
        self.session: Optional[Session] = None
        super().__init__(reconnect_delay=reconnect_delay, host=host, port=port, user=user, password=password, **kwargs)

    def connect(self) -> None:
        try:
            self.session = Session(**self._connection_params)
            self.session.open()
            self.session.execute_query_statement("SHOW STORAGE GROUP").close_operation_handle()
            self._last_success_time = datetime.now()
            logging.info("[IoTDBClient] Connected successfully.")
        except Exception as e:
            raise DBConnectionError("IoTDBClient.connect", "iotdb", str(e)) from e

    def close(self) -> None:
        if self.session:
            try:
                self.session.close()
                logging.info("[IoTDBClient] Connection closed.")
            except Exception as e:
                logging.warning(f"[IoTDBClient] Close failed: {e}")
            finally:
                self.session = None

    def _get_session(self):
        if self.session is None:
            raise DBConnectionError("IoTDBClient.execute", "iotdb", "Not connected")
        return self.session

    def _execute_core(self, session, sql: str, sql_type: str) -> Union[pd.DataFrame, int, None]:
        if sql_type != "query":
            session.execute_non_query_statement(sql)
            return 1
        result = session.execute_query_statement(sql)
        df = result.todf()
        result.close_operation_handle()
        return df if df is not None and not df.empty else None

    def _check_and_reconnect(self, session) -> None:
        now = datetime.now()
        if self._last_success_time is None:
            self._last_success_time = now
            return
        if now - self._last_success_time > self._reconnect_delay:
            try:
                session.execute_query_statement("SHOW STORAGE GROUP").close_operation_handle()
                self._last_success_time = now
                logging.info(f"[{self.__class__.__name__}] Ping successful.")
            except Exception:
                logging.warning(f"[{self.__class__.__name__}] Ping failed, reconnecting...")
                self.close()
                self.connect()
                self._last_success_time = datetime.now()


class IoTDBPoolClient(IoTDBBaseClient):
    """
    IoTDBPoolClient - IoTDB 线程池客户端
    Version: 0.1.2
    """

    def __init__(self, host: str, port: int, user: str, password: str, max_pool_size: int = 10,
                 wait_timeout_in_ms: int = 3000, reconnect_delay: int = 10, **kwargs):
        self.pool: Optional[SessionPool] = None
        super().__init__(
            reconnect_delay=reconnect_delay,
            host=host,
            port=port,
            user=user,
            password=password,
            max_pool_size=max_pool_size,
            wait_timeout_in_ms=wait_timeout_in_ms,
            **kwargs,
        )

    def connect(self) -> None:
        try:
            config = PoolConfig(
                host=self._connection_params["host"],
                port=str(self._connection_params["port"]),
                user_name=self._connection_params["user"],
                password=self._connection_params["password"],
                **{k: v for k, v in self._connection_params.items()
                   if k not in {"host", "port", "user", "password", "max_pool_size", "wait_timeout_in_ms"}},
            )
            self.pool = create_session_pool(
                config,
                max_pool_size=self._connection_params.get("max_pool_size", 10),
                wait_timeout_in_ms=self._connection_params.get("wait_timeout_in_ms", 3000),
            )
            session = self.pool.get_session()
            try:
                session.execute_query_statement("SHOW STORAGE GROUP").close_operation_handle()
            finally:
                self.pool.put_back(session)
            self._last_success_time = datetime.now()
            logging.info("[IoTDBPoolClient] Connected successfully.")
        except Exception as e:
            raise DBConnectionError("IoTDBPoolClient.connect", "iotdb", str(e)) from e

    def close(self) -> None:
        if self.pool:
            try:
                self.pool.close()
                logging.info("[IoTDBPoolClient] Connection closed.")
            except Exception as e:
                logging.warning(f"[IoTDBPoolClient] Close failed: {e}")
            finally:
                self.pool = None

    def _get_session(self):
        if self.pool is None:
            raise DBConnectionError("IoTDBPoolClient.execute", "iotdb", "Not connected")
        return self.pool.get_session()

    def _return_session(self, session) -> None:
        if self.pool is None or session is None:
            return
        try:
            self.pool.put_back(session)
        except Exception as e:
            logging.warning(f"[IoTDBPoolClient] Failed to return session: {e}")

    def _execute_core(self, session, sql: str, sql_type: str) -> Union[pd.DataFrame, int, None]:
        if sql_type != "query":
            session.execute_non_query_statement(sql)
            self._last_success_time = datetime.now()
            return 1
        result = session.execute_query_statement(sql)
        df = result.todf()
        result.close_operation_handle()
        self._last_success_time = datetime.now()
        return df if df is not None and not df.empty else None

    def _check_and_reconnect(self, session) -> None:
        now = datetime.now()
        if self.pool is None:
            logging.warning("[IoTDBPoolClient] Pool is None, reconnecting...")
            self.connect()
            return
        if session is None:
            logging.warning("[IoTDBPoolClient] Session is None, skipping ping.")
            return
        if self._last_success_time is None:
            self._last_success_time = now
            return
        if now - self._last_success_time > self._reconnect_delay:
            try:
                session.execute_query_statement("SHOW STORAGE GROUP").close_operation_handle()
                self._last_success_time = now
                logging.info("[IoTDBPoolClient] Ping successful, connection kept alive.")
            except Exception:
                logging.warning("[IoTDBPoolClient] Ping failed, reconnecting...")
                self.close()
                self.connect()
                self._last_success_time = datetime.now()
