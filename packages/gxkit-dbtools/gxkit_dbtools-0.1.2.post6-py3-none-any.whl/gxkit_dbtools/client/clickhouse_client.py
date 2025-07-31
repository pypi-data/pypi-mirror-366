import logging
import time
from datetime import datetime, timedelta
from typing import Optional, List, Iterator, Sequence, Union, Tuple

import pandas as pd
from clickhouse_driver import Client
from clickhouse_driver.errors import Error as ClickHouseError

from gxkit_dbtools.parser.sql_parser import SQLParser
from gxkit_dbtools.client.utils import clean_dataframe_clickhouse, to_python_values
from gxkit_dbtools.client.base import BaseDBClient
from gxkit_dbtools.exception import DBConnectionError, SQLExecutionError


class ClickHouseClient(BaseDBClient):
    """
    ClickHouseClient - ClickHouse 基础客户端
    Version: 0.1.2
    """

    def __init__(self, host: str, port: int, user: str, password: str, database: str,
                 reconnect_delay: int = 10, **kwargs):
        self.client: Optional[Client] = None
        self.db_type: str = "clickhouse"
        self._last_success_time: Optional[datetime] = None
        self._reconnect_delay: timedelta = timedelta(minutes=reconnect_delay)
        self._connection_params = dict(host=host, port=port, user=user,
                                       password=password, database=database, **kwargs)
        self.connect()

    def connect(self) -> None:
        try:
            self.client = Client(**self._connection_params)
            self.client.execute("SELECT 1")
            self._last_success_time = datetime.now()
            logging.info("[ClickHouseClient] Connected successfully.")
        except Exception as e:
            raise DBConnectionError("ClickHouseClient.connect", "clickhouse", str(e)) from e

    def close(self) -> None:
        if self.client:
            try:
                self.client.disconnect()
                logging.info("[ClickHouseClient] Connection closed.")
            except Exception as e:
                logging.warning(f"[ClickHouseClient] Close failed: {e}")
            finally:
                self.client = None

    def upload(self, df: pd.DataFrame, table_name: str, columns: Optional[List[str]] = None,
               batch_size: int = 10000) -> None:
        df = df.copy()
        if columns is None:
            columns = df.columns
        else:
            df = df[columns]
        df = clean_dataframe_clickhouse(df)
        columns_str = ", ".join(f"`{col}`" for col in columns)
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES"
        for start in range(0, len(df), batch_size):
            batch_df = df.iloc[start:start + batch_size]
            values = to_python_values(batch_df)
            try:
                self.execute(sql, values=values)
            except Exception as e:
                logging.error(
                    f"[ClickHouseClient.upload] Failed to insert batch into {table_name}: {e}")
                raise SQLExecutionError("ClickHouseClient.upload", f"{sql}...", str(e)) from e

    def execute(self, sql: str, values: Optional[List[Tuple]] = None, max_retry: int = 3) -> Union[
        pd.DataFrame, int, None]:
        if self.client is None:
            raise DBConnectionError("ClickHouseClient.execute", "clickhouse", "Not connected")

        sql = sql.strip()
        parsed_sql = SQLParser(f"{sql} (null)" if values else sql, db_type="clickhouse")
        sql_type = parsed_sql.sql_type()

        if values is not None:
            if not sql.lower().endswith("values"):
                raise SQLExecutionError("ClickHouseClient.execute", sql,
                                        "values mode requires SQL to end with 'VALUES'")

            if sql_type != "statement":
                raise SQLExecutionError("ClickHouseClient.execute", sql,
                                        f"values mode only supports statement SQL, got sql_type={sql_type}")

        for attempt in range(1, max_retry + 1):
            try:
                return self._execute_core(sql, sql_type, values)
            except ClickHouseError as e:
                logging.warning(f"[ClickHouseClient] Retry {attempt}/{max_retry} on {sql_type} | {e}")
                self.close()
                self.connect()
                time.sleep(0.5)
            except Exception as e:
                raise SQLExecutionError("ClickHouseClient.execute", sql, str(e)) from e

        raise SQLExecutionError("ClickHouseClient.execute", sql, f"Failed after {max_retry} retries")

    def _execute_core(self, sql: str, sql_type: str, values: Optional[List[Tuple]] = None) -> Union[
        pd.DataFrame, int, None]:
        self._check_and_reconnect()
        try:
            if sql_type == "query":
                result, meta = self.client.execute(sql, with_column_types=True)
                if not result:
                    return None
                columns = [col[0] for col in meta]
                self._last_success_time = datetime.now()
                return pd.DataFrame(result, columns=columns)

            elif values is not None:
                self.client.execute(sql, values)
                self._last_success_time = datetime.now()
                return len(values)

            else:
                self.client.execute(sql)
                self._last_success_time = datetime.now()
                return 1
        except Exception as e:
            raise SQLExecutionError("ClickHouseClient._execute_core", sql, str(e)) from e

    def _check_and_reconnect(self):
        now = datetime.now()

        if self.client is None:
            logging.warning("[ClickHouseClient] Client is None, reconnecting...")
            self.connect()
            return

        if self._last_success_time is None:
            self._last_success_time = now
            return

        if now - self._last_success_time > self._reconnect_delay:
            try:
                self.client.connection.ping()
                self._last_success_time = now
                logging.info("[ClickHouseClient] Ping successful, connection kept alive.")
            except Exception:
                logging.warning("[ClickHouseClient] Ping failed, reconnecting...")
                self.close()
                self.connect()
                self._last_success_time = datetime.now()
