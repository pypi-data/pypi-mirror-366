"""
dbtools.parser 工具层
Version 0.1.0
"""

MULTIWORD_COMMAND_OPS = {
    # MySQL
    "show databases", "show tables", "show full tables", "show create table", "show table status", "show columns",
    "show columns from", "show full columns from", "show indexes", "show indexes from", "show keys from",
    "show processlist", "show status", "show engine status", "show engines", "show grants", "show master status",
    "show slave status", "show binary logs", "show binlog events", "show open tables", "show privileges",
    "show variables", "show global status", "show session status", "show global variables", "show session variables",
    "show warnings", "show errors",

    # ClickHouse
    "show tables", "show databases", "show create table", "show create database", "show settings", "show functions",
    "show clusters", "show macros", "show dictionaries", "show engines", "show indexes", "show policies", "show quota",
    "show roles", "show users", "show profile events", "show profile events histogram", "show profile events values",

    # IoTDB
    "show timeseries", "show child paths", "show child nodes", "show devices", "show storage group",
    "show storage groups", "show ttl", "show cluster", "show version", "show triggers", "show functions",
    "show schema templates", "show measurements", "show data type", "show region", "show regions", "show pipe",
    "show pipes", "show queries", "show count timeseries", "show count devices", "show paths using template",

    # 通用 command
    "explain analyze", "reset query cache", "flush privileges", "lock tables", "unlock tables", "set global",
    "set session", "set names", "set character set", "kill query", "kill connection", "analyze table", "repair table",
    "optimize table", "truncate table",
}

QUERY_OPS = {
    "select", "show", "explain", "desc", "describe", "use", "help", "analyze", "union", "intersect", "except", "with"
}

STATEMENT_OPS = {
    # 数据写入/更新
    "insert", "update", "delete", "replace", "merge",
    # DDL（数据定义语言）
    "create", "drop", "alter", "rename", "comment",
    "truncate", "truncatetable", "optimize", "check", "repair",
    # 权限管理
    "grant", "revoke",
    # 事务控制
    "begin", "start", "commit", "rollback", "savepoint", "release",
    # 系统设置
    "set", "reset", "flush", "kill",
    # 存储过程与执行计划
    "call", "prepare", "execute", "deallocate",
    # 并发控制
    "lock", "unlock",
    # 特殊数据库操作
    "vacuum", "load", "analyze table"
}

FIXED_COLUMNS = {
    "mysql": {
        "explain": [
            "id", "select_type", "table", "partitions", "type", "possible_keys",
            "key", "key_len", "ref", "rows", "filtered", "Extra"
        ],
        "show tables": ["Tables_in_{database}"],
        "show databases": ["Database"],
        "show columns": ["Field", "Type", "Null", "Key", "Default", "Extra"],
        "show columns from": ["Field", "Type", "Null", "Key", "Default", "Extra"],
        "show full columns from": ["Field", "Type", "Collation", "Null", "Key", "Default", "Extra", "Privileges",
                                   "Comment"],
        "show index": ["Table", "Non_unique", "Key_name", "Seq_in_index", "Column_name",
                       "Collation", "Cardinality", "Sub_part", "Packed", "Null", "Index_type",
                       "Comment", "Index_comment"],
        "show indexes": ["Table", "Non_unique", "Key_name", "Seq_in_index", "Column_name",
                         "Collation", "Cardinality", "Sub_part", "Packed", "Null", "Index_type",
                         "Comment", "Index_comment"],
        "show indexes from": ["Table", "Non_unique", "Key_name", "Seq_in_index", "Column_name",
                              "Collation", "Cardinality", "Sub_part", "Packed", "Null", "Index_type",
                              "Comment", "Index_comment"],
        "show keys from": ["Table", "Non_unique", "Key_name", "Seq_in_index", "Column_name",
                           "Collation", "Cardinality", "Sub_part", "Packed", "Null", "Index_type",
                           "Comment", "Index_comment"],
        "show processlist": ["Id", "User", "Host", "db", "Command", "Time", "State", "Info"],
        "show status": ["Variable_name", "Value"],
        "show global status": ["Variable_name", "Value"],
        "show session status": ["Variable_name", "Value"],
        "show variables": ["Variable_name", "Value"],
        "show global variables": ["Variable_name", "Value"],
        "show session variables": ["Variable_name", "Value"],
        "show privileges": ["Privilege", "Context", "Comment"],
        "show grants": ["Grants for user"],
        "show binary logs": ["Log_name", "File_size"],
        "show master status": ["File", "Position", "Binlog_Do_DB", "Binlog_Ignore_DB", "Executed_Gtid_Set"],
        "show slave status": ["Slave_IO_State", "Master_Host", "Master_User", "Master_Port", "Connect_Retry"],
        "show open tables": ["Database", "Table", "In_use", "Name_locked"],
        "show create table": ["Table", "Create Table"],
        "show engines": ["Engine", "Support", "Comment", "Transactions", "XA", "Savepoints"],
        "show engine status": ["Type", "Name", "Status"],
        "show errors": ["Level", "Code", "Message"],
        "show warnings": ["Level", "Code", "Message"],
        "show table status": ["Name", "Engine", "Version", "Row_format", "Rows", "Avg_row_length", "Data_length",
                              "Max_data_length", "Index_length", "Data_free", "Auto_increment", "Create_time",
                              "Update_time", "Check_time", "Collation", "Checksum", "Create_options", "Comment"],
        "describe": ["Field", "Type", "Null", "Key", "Default", "Extra"],
    },

    "clickhouse": {
        "explain": ["explain"],
        "show tables": ["name"],
        "show databases": ["name"],
        "show create table": ["statement"],
        "show create database": ["statement"],
        "show settings": ["name", "value", "changed", "description"],
        "show functions": ["name"],
        "show macros": ["macro", "value"],
        "show users": ["name"],
        "show roles": ["name"],
        "show quota": ["name"],
        "show policies": ["name"],
        "show clusters": ["cluster"],
        "show indexes": ["table", "name", "type", "expr", "granularity"],
        "show engines": ["name", "description"],
        "show dictionaries": ["name", "origin", "structure", "layout", "status"],
        "show profile events": ["event", "value"],
        "show profile events histogram": ["event", "bucket", "count"],
        "show profile events values": ["event", "value"],
        "describe": ["name", "type", "default_type", "default_expression", "comment", "codec_expression",
                     "ttl_expression"],
    },

    "iotdb": {
        "explain": ["operator", "plan", "details"],
        "show timeseries": ["timeseries", "alias", "database", "dataType", "encoding", "compression", "tags",
                            "attributes"],
        "show devices": ["devices", "isAligned"],
        "show child paths": ["childPaths"],
        "show child nodes": ["childNodes"],
        "show storage group": ["storageGroup"],
        "show storage groups": ["storageGroup"],
        "show ttl": ["storageGroup", "ttl"],
        "show cluster": ["NodeID", "Internal IP", "Port", "Role"],
        "show version": ["version"],
        "show triggers": ["triggerName", "status", "path", "className"],
        "show pipes": ["PipeName", "Role", "Status"],
        "show pipe": ["PipeName", "Role", "Status"],
        "show functions": ["function name", "class name"],
        "show schema templates": ["template name"],
        "show measurements": ["measurement"],
        "show data type": ["path", "dataType"],
        "show region": ["Region ID", "Type", "Status"],
        "show regions": ["Region ID", "Type", "Status"],
        "show queries": ["queryId", "statement", "startTime", "executionTime"],
        "show count timeseries": ["count"],
        "show count devices": ["count"],
        "show paths using template": ["path", "templateName"],
        "describe": ["timeseries", "alias", "database", "dataType", "encoding", "compression", "tags", "attributes"],
    }
}
