import logging
import time
from datetime import datetime, timedelta
from typing import Optional, List, Sequence, Union

import pandas as pd
import pymysql
from pymysql.cursors import Cursor

from gxkit_dbtools.parser.sql_parser import SQLParser
from gxkit_dbtools.client.utils import clean_dataframe_mysql
from gxkit_dbtools.client.base import BaseDBClient
from gxkit_dbtools.exception import DBConnectionError, SQLExecutionError


class MySQLClient(BaseDBClient):
    """
    MySQLClient - MySQL 基础客户端
    Version: 0.1.2
    """

    def __init__(self, host: str, port: int, user: str, password: str, database: str,
                 reconnect_delay: int = 10, **kwargs):
        self.client: Optional[pymysql.connections.Connection] = None
        self.database = database
        self._last_success_time: Optional[datetime] = None
        self._reconnect_delay: timedelta = timedelta(minutes=reconnect_delay)
        self._connection_params = dict(host=host, port=port, user=user, password=password,
                                       database=database, autocommit=True, **kwargs)
        self.connect()

    def connect(self) -> None:
        try:
            self.client = pymysql.connect(**self._connection_params)
            with self.client.cursor() as cursor:
                cursor.execute("SELECT 1")
            self._last_success_time = datetime.now()
            logging.info("[MySQLClient] Connected successfully.")
        except Exception as e:
            raise DBConnectionError("MySQLClient.connect", "mysql", str(e)) from e

    def close(self):
        if self.client:
            try:
                self.client.close()
                logging.info("[MySQLClient] Connection closed.")
            except Exception as e:
                logging.warning(f"[MySQLClient] Close failed: {e}")
            finally:
                self.client = None

    def upload(self, df: pd.DataFrame, table_name: str, columns: Optional[List[str]] = None,
               batch_size: int = 10000) -> None:
        df = df.copy()
        if columns is None:
            columns = df.columns
        else:
            df = df[columns]
        df = clean_dataframe_mysql(df)
        columns_str = ", ".join(f"`{col}`" for col in columns)
        for start in range(0, len(df), batch_size):
            batch = df.iloc[start:start + batch_size]
            values = ", ".join([f"({', '.join(map(str, row))})" for row in batch.values])
            sql = f"INSERT INTO {table_name} ({columns_str}) VALUES {values};"
            try:
                self.execute(sql=sql)
            except Exception as e:
                logging.error(
                    f"[MySQLClient.upload] Failed to insert batch into {table_name}: {e}")
                raise SQLExecutionError("MySQLClient.upload", sql, str(e)) from e

    def execute(self, sql: str, max_retry: int = 3) -> Union[pd.DataFrame, int, None]:
        parsed_sql = SQLParser(sql, db_type="mysql")
        sql_type = parsed_sql.sql_type()
        for attempt in range(1, max_retry + 1):
            try:
                return self._execute_core(sql, sql_type)
            except (pymysql.err.OperationalError, pymysql.err.InterfaceError) as e:
                logging.warning(f"[MySQLClient] Retry {attempt}/{max_retry} on {sql_type} | {e}")
                self.close()
                self.connect()
                time.sleep(0.5)
        raise SQLExecutionError("MySQLClient.execute", sql, f"Failed after {max_retry} retries")

    def _execute_core(self, sql: str, sql_type: str) -> Union[pd.DataFrame, int, None]:
        self._check_and_reconnect()
        try:
            with self.client.cursor(Cursor) as cursor:
                cursor.execute(sql)
                self._last_success_time = datetime.now()
                if sql_type == "query":
                    result = cursor.fetchall()
                    if not result:
                        return None
                    column_names = [desc[0] for desc in cursor.description]
                    return pd.DataFrame.from_records(result, columns=column_names)
                else:
                    return 1
        except Exception as e:
            raise SQLExecutionError("MySQLClient._execute_core", sql, str(e)) from e

    def _check_and_reconnect(self):
        now = datetime.now()

        if self.client is None:
            logging.warning("[MySQLClient] Client is None, reconnecting...")
            self.connect()
            return

        if self._last_success_time is None:
            self._last_success_time = now
            return

        if now - self._last_success_time > self._reconnect_delay:
            if getattr(self.client, "_sock", None) is None:
                logging.warning("[MySQLClient] Socket closed, reconnecting...")
                self.close()
                self.connect()
                return
            try:
                self.client.ping(reconnect=True)
                self._last_success_time = now
                logging.info("[MySQLClient] Ping successful, connection kept alive.")
            except Exception:
                logging.warning("[MySQLClient] Ping failed, reconnecting...")
                self.close()
                self.connect()
                self._last_success_time = datetime.now()
