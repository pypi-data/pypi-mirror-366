import re
import logging

import sqlglot
from sqlglot import expressions as exp
from sqlglot.errors import ParseError
from typing import List, Optional, Tuple, Dict, Union, Literal

from gxkit_dbtools.exception import SQLParseError
from gxkit_dbtools.parser.utils import MULTIWORD_COMMAND_OPS, QUERY_OPS, STATEMENT_OPS, FIXED_COLUMNS

logging.getLogger("sqlglot").setLevel(logging.ERROR)


class SQLParser:
    """
    SQLParser - SQL 超级解析器
    Version: 0.1.0
    """

    def __init__(self, sql: str, db_type: str = "mysql"):
        self.original_db_type = db_type
        self.db_type = db_type if db_type != "iotdb" else None
        self._sql_type: Optional[str] = None
        self._spec_flag: bool = False
        self._cache: Dict[str, Union[List[str], List[Tuple[str, str]], Dict[str, List[str]]]] = {}
        self._iotdb_paths: List[str] = []
        self.raw_sql, self.ast = self._parse(sql)
        self._operation, self._spec_flag = self._init_operation()

    def __str__(self) -> str:
        return self.raw_sql

    def __repr__(self) -> str:
        return f"<SQLParser: {self.operation().upper()} - {self.raw_sql}>"

    def _init_operation(self) -> Tuple[str, bool]:
        if self.ast.key and self.ast.key.lower() != "command":
            return self.ast.key.lower(), False
        return self._extract_spec_operation(), True

    def sql(self) -> str:
        sql = self.ast.sql(dialect=self.db_type)
        return self._restore_iotdb_paths(sql)

    def operation(self) -> str:
        return self._operation

    def sql_type(self) -> str:
        if self._sql_type is None:
            op_lower = self._operation
            if any(op_lower.startswith(q) for q in QUERY_OPS):
                self._sql_type = "query"
            elif any(op_lower.startswith(s) for s in STATEMENT_OPS):
                self._sql_type = "statement"
            else:
                self._sql_type = "unknown"
        return self._sql_type

    def tables(self, subquery: bool = False) -> List[str]:
        if self._spec_flag:
            if "tables:spec" not in self._cache:
                self._cache["tables:spec"] = self._extract_spec_table()
            return self._cache["tables:spec"]

        if "tables:main" not in self._cache or "tables:sub" not in self._cache:
            main_tables, subquery_tables = [], []
            for table_node in self.ast.find_all(exp.Table):
                catalog = table_node.args.get("catalog")
                db = table_node.args.get("db")
                name_expr = table_node.args.get("this")
                if not name_expr:
                    continue
                parts = []
                if catalog is not None:
                    parts.append(catalog.this)
                if db is not None:
                    parts.append(db.this)
                parts.append(name_expr.sql(dialect=self.db_type))
                table_name = ".".join(parts)
                table_name = table_name.replace("`", "").replace('"', "").replace("'", "")
                if table_node.find_ancestor(exp.Subquery):
                    subquery_tables.append(table_name)
                else:
                    main_tables.append(table_name)
            self._cache["tables:main"] = main_tables
            self._cache["tables:sub"] = subquery_tables
        return (
            self._cache["tables:main"] + self._cache["tables:sub"]
            if subquery
            else self._cache["tables:main"]
        )

    def columns(self, mode: Literal["raw", "alias", "full"] = "full", prefix: bool = False,
                db_type: Optional[str] = None) -> Union[List[str], List[Tuple[str, str]]]:
        if self.sql_type() != "query":
            return []

        db = (db_type or self.original_db_type or self.db_type or "").lower()
        key = f"columns:{mode}:prefix_{prefix}"

        if key not in self._cache:
            full_key = f"columns:full:prefix_{prefix}"
            if full_key not in self._cache:
                if self._operation == "select":
                    full_data = self._extract_select_columns(prefix)
                elif db in FIXED_COLUMNS and self._operation in FIXED_COLUMNS[db]:
                    full_data = [(col, col) for col in FIXED_COLUMNS[db][self._operation]]
                else:
                    full_data = []
                self._cache[full_key] = full_data
            else:
                full_data = self._cache[full_key]
            self._cache[f"columns:raw:prefix_{prefix}"] = [raw for raw, _ in full_data]
            self._cache[f"columns:alias:prefix_{prefix}"] = [alias for _, alias in full_data]

        return self._cache[key]

    def segments(self, seg_type: Union[str, List[str]] = "all", subquery: bool = False) -> Dict[str, List[str]]:
        def add_segment(segment: str, value: str):
            result.setdefault(segment, []).append(value)

        valid_seg_type = {
            "where": exp.Where,
            "group": exp.Group,
            "having": exp.Having,
            "order": exp.Order,
            "limit": exp.Limit,
            "offset": None
        }
        # 解析 seg_type 参数
        if seg_type == "all":
            seg_types = list(valid_seg_type.keys())
        elif isinstance(seg_type, str):
            seg_types = [seg_type.lower()]
        else:
            seg_types = [c.lower() for c in seg_type]
        seg_types = [c for c in seg_types if c in valid_seg_type]
        if not seg_types:
            raise SQLParseError("dbtools.SQLParser._parse", self.raw_sql,
                                f"No valid segment types provided. Supported: {list(valid_seg_type.keys())}")

        result: Dict[str, List[str]] = {}
        for seg in seg_types:
            cache_key = f"segments:{seg}:subquery_{subquery}"
            if cache_key in self._cache:
                for val in self._cache[cache_key]:
                    add_segment(seg, val)
                continue
            # offset 特判处理
            if seg == "offset":
                offsets = self._extract_offset(subquery=subquery)
                offsets = [offsets] if isinstance(offsets, str) else offsets or []
                self._cache[cache_key] = offsets
                for val in offsets:
                    add_segment(seg, val)
                continue
            # 生成并缓存其他子句
            segment_values: List[str] = []
            top_expr = self.ast.args.get(seg)
            if top_expr:
                segment_values.append(top_expr.sql(dialect=self.db_type))
                if seg == "limit" and isinstance(top_expr, exp.Limit):
                    offset_expr = top_expr.args.get("offset")
                    if offset_expr:
                        offset_clause = offset_expr.sql(dialect=self.db_type)
                        self._cache.setdefault(f"segments:offset:subquery_{subquery}", []).append(offset_clause)
            if subquery:
                top_id = id(top_expr) if top_expr else None
                for expr in self.ast.find_all(valid_seg_type[seg]):
                    if id(expr) == top_id:
                        continue
                    segment_values.append(expr.sql(dialect=self.db_type))
                    if seg == "limit" and isinstance(expr, exp.Limit):
                        offset_expr = expr.args.get("offset")
                        if offset_expr:
                            offset_clause = offset_expr.sql(dialect=self.db_type)
                            self._cache.setdefault(f"segments:offset:subquery_{subquery}", []).append(offset_clause)
            self._cache[cache_key] = segment_values
            for val in segment_values:
                add_segment(seg, val)

        return result

    def change_segments(self, replacements: Dict[str, str]) -> str:
        new_ast = self.ast.copy()

        # 每种操作对应的支持子句
        operation = self.operation().lower()
        allowed_segments_by_op = {
            "select": {"where", "group", "having", "order", "limit", "offset"},
            "insert": set(),
            "update": {"where"},
            "delete": {"where"},
        }
        allowed_segments = allowed_segments_by_op.get(operation, set())
        # 映射 segment -> AST 类型
        seg_expr_map = {
            "where": exp.Where,
            "group": exp.Group,
            "having": exp.Having,
            "order": exp.Order,
            "limit": exp.Limit,
        }
        for seg, raw_sql in replacements.items():
            seg = seg.lower()
            if seg not in allowed_segments:
                raise SQLParseError("change_segments", self.raw_sql,
                                    f"Segment '{seg}' is not allowed for operation '{operation}'")
            if seg == "offset":
                continue
            if seg not in seg_expr_map:
                raise SQLParseError("change_segments", self.raw_sql, f"Unsupported segment type: '{seg}'")

            # 去除 segment 前缀
            prefix = seg.upper().replace("GROUP", "GROUP BY").replace("ORDER", "ORDER BY")
            cleaned_sql = re.sub(rf"^\s*{seg}\b\s*", "", raw_sql.strip(), flags=re.IGNORECASE)
            inject_sql = f"SELECT * FROM dummy {prefix} {cleaned_sql}"
            try:
                inject_ast = sqlglot.parse_one(inject_sql)
            except Exception as e:
                raise SQLParseError("change_segments", inject_sql, f"Invalid SQL for segment '{seg}': {e}")

            seg_expr = inject_ast.args.get(seg)
            if not seg_expr:
                raise SQLParseError("change_segments", inject_sql, f"Segment '{seg}' parse failed from injected SQL.")

            new_ast.set(seg, seg_expr)
        # 初步生成 SQL
        new_sql = new_ast.sql(dialect=self.db_type)
        new_sql = self._restore_iotdb_paths(new_sql)
        # 单独处理 OFFSET
        if "offset" in replacements:
            if "offset" not in allowed_segments:
                raise SQLParseError("change_segments", self.raw_sql,
                                    f"Segment 'offset' is not allowed for operation '{operation}'")

            new_offset = re.sub(r"^\s*offset\b\s*", "", replacements["offset"].strip(), flags=re.IGNORECASE)
            if re.search(r"\bOFFSET\b\s+\d+", new_sql, flags=re.IGNORECASE):
                new_sql = re.sub(r"\bOFFSET\b\s+\d+", f"OFFSET {new_offset}", new_sql, flags=re.IGNORECASE)
            else:
                new_sql += f" OFFSET {new_offset}"
        return new_sql

    def change_columns(self, columns: Union[str, List[str]]) -> str:
        operation = self.operation().lower()
        if operation != "select":
            raise SQLParseError(
                "change_columns",
                self.raw_sql,
                "Only SELECT statements support changing columns",
            )

        cols_sql = ", ".join(columns) if isinstance(columns, list) else columns
        inject_sql = f"SELECT {cols_sql} FROM dummy"
        try:
            inject_ast = sqlglot.parse_one(inject_sql, dialect=self.db_type)
        except Exception as e:
            raise SQLParseError(
                "change_columns",
                inject_sql,
                f"Invalid column expressions: {e}",
            )

        exprs = inject_ast.args.get("expressions") or []
        if not exprs:
            raise SQLParseError(
                "change_columns",
                inject_sql,
                "Failed to parse column expressions",
            )

        new_ast = self.ast.copy()
        new_ast.set("expressions", exprs)
        new_sql = new_ast.sql(dialect=self.db_type)
        return self._restore_iotdb_paths(new_sql)

    def _parse(self, sql: str) -> tuple[str, exp.Expression]:
        try:
            sql_clean = self._clean_sql(sql)
            ast = sqlglot.parse_one(sql_clean, dialect=self.db_type)
        except ParseError as e:
            raise SQLParseError("dbtools.SQLParser._parse", sql, f"SQL syntax error: {e}") from e
        except Exception as e:
            raise SQLParseError("dbtools.SQLParser._parse", sql, f"SQL unknown error: {e}") from e
        return sql_clean, ast

    def _clean_sql(self, sql: str) -> str:
        # 鲁棒的去除注释
        sql = self._remove_sql_comments(sql)
        # 替换全角字符 → 半角
        sql = ''.join(
            chr(ord(char) - 0xFEE0) if 0xFF01 <= ord(char) <= 0xFF5E else char
            for char in sql
        )
        # 替换常见中文符号
        sql = sql.replace('，', ',').replace('）', ')').replace('（', '(').replace('：', ':') \
            .replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"')
        # IoTDB 特殊路径预处理
        if self.original_db_type == "iotdb":
            sql, self._iotdb_paths = self._quote_iotdb_paths(sql)
        # 合并多余空格
        return re.sub(r"\s+", " ", sql).strip()

    def _extract_spec_operation(self) -> str:
        tokens = self.raw_sql.strip().lower().split()
        for n in range(min(4, len(tokens)), 0, -1):
            candidate = " ".join(tokens[:n])
            if candidate in MULTIWORD_COMMAND_OPS:
                return candidate
        return tokens[0] if tokens else "command"

    def _extract_spec_table(self) -> List[str]:
        tables = []
        # IoTDB 特殊表名匹配
        match = re.search(r"(root\.[\w\.\*]+)", self.raw_sql)
        if match:
            tables = [match.group(1)]
        # 普通匹配
        if not tables:
            operation = self._operation
            if operation.startswith("show"):
                tables = self.extract_after_keywords(self.raw_sql, [
                    "show create table", "show columns from", "show columns in", "show index from",
                    "show indexes from", "show keys from", "show full columns from", "show extended columns from"
                ])
            elif operation == "explain":
                match = re.search(r"from\s+([`\"']?\w+(?:[.`\"']\w+)?[`\"']?)", self.raw_sql, flags=re.IGNORECASE)
                if match:
                    tables = [match.group(1).replace("`", "").replace('"', "").replace("'", "")]
            elif operation in {"truncate", "truncatetable"}:
                tables = self.extract_after_keywords(self.raw_sql, ["truncate table", "truncate"])
            elif operation == "use":
                match = re.match(r"use\s+([`\"']?\w+[`\"']?)", self.raw_sql, flags=re.IGNORECASE)
                if match:
                    tables = [match.group(1).replace("`", "").replace('"', "").replace("'", "")]
        return tables

    def _extract_select_columns(self, prefix: bool) -> List[Tuple[str, str]]:
        result = []
        for expr in self.ast.expressions:
            if isinstance(expr, exp.Star):
                result.append(("*", "*"))
            elif isinstance(expr, exp.Alias):
                raw_expr = expr.this
                if isinstance(raw_expr, exp.Column):
                    raw_name = raw_expr.sql() if prefix else raw_expr.name
                else:
                    raw_name = raw_expr.sql()
                alias_name = expr.alias_or_name or raw_name
                result.append((raw_name, alias_name))
            elif isinstance(expr, exp.Column):
                raw_name = expr.sql() if prefix else expr.name
                alias_name = expr.name
                result.append((raw_name, alias_name))
            else:
                raw_name = expr.sql()
                alias_name = raw_name
                result.append((raw_name, alias_name))
        return result

    def _extract_offset(self, subquery: bool = False) -> Union[Optional[str], List[str]]:
        def get_offset_from_limit(expr: exp.Limit) -> Optional[str]:
            off = expr.args.get("offset")
            return off.sql(dialect=self.db_type) if off else None

        offsets: List[str] = []

        top_offset = self.ast.args.get("offset")
        if isinstance(top_offset, exp.Offset):
            offsets.append(top_offset.sql(dialect=self.db_type))

        top_limit = self.ast.args.get("limit")
        if isinstance(top_limit, exp.Limit):
            off_sql = get_offset_from_limit(top_limit)
            if off_sql:
                offsets.append(off_sql)

        if subquery:
            top_offset_id = id(top_offset) if isinstance(top_offset, exp.Offset) else None
            top_limit_id = id(top_limit) if isinstance(top_limit, exp.Limit) else None
            for expr in self.ast.find_all(exp.Offset):
                if id(expr) == top_offset_id:
                    continue
                offsets.append(expr.sql(dialect=self.db_type))
            for expr in self.ast.find_all(exp.Limit):
                if id(expr) == top_limit_id:
                    continue
                off_sql = get_offset_from_limit(expr)
                if off_sql:
                    offsets.append(off_sql)

        return offsets if subquery else (offsets[0] if offsets else None)

    @staticmethod
    def extract_after_keywords(sql: str, keywords: List[str]) -> List[str]:
        lowered_sql = sql.lower()
        for keyword in keywords:
            if keyword not in lowered_sql:
                continue
            pattern = rf"{keyword}\s+([`\"']?\w+(?:[.`\"']\w+)?[`\"']?)"
            match = re.search(pattern, sql, flags=re.IGNORECASE)
            if match:
                return [match.group(1).replace("`", "").replace('"', "").replace("'", "")]
        return []

    @staticmethod
    def _remove_sql_comments(sql: str) -> str:
        result = []
        i = 0
        in_single_quote = False
        in_double_quote = False
        in_line_comment = False
        in_block_comment = False
        length = len(sql)
        while i < length:
            char = sql[i]
            next_char = sql[i + 1] if i + 1 < length else ""
            # 进入字符串状态
            if not in_line_comment and not in_block_comment:
                if not in_double_quote and char == "'":
                    result.append(char)
                    in_single_quote = not in_single_quote
                    i += 1
                    continue
                elif not in_single_quote and char == '"':
                    result.append(char)
                    in_double_quote = not in_double_quote
                    i += 1
                    continue
            # 忽略字符串中的内容
            if in_single_quote or in_double_quote:
                result.append(char)
                i += 1
                continue
            # 开始 block 注释
            if not in_line_comment and not in_block_comment and char == "/" and next_char == "*":
                in_block_comment = True
                i += 2
                continue
            # 结束 block 注释
            if in_block_comment and char == "*" and next_char == "/":
                in_block_comment = False
                i += 2
                continue
            # 开始 line 注释
            if not in_line_comment and not in_block_comment and char == "-" and next_char == "-":
                in_line_comment = True
                i += 2
                continue
            # 结束 line 注释（遇到换行）
            if in_line_comment and char in "\n\r":
                in_line_comment = False
                result.append(char)
                i += 1
                continue
            # 默认追加字符（不在注释中）
            if not in_line_comment and not in_block_comment:
                result.append(char)
            i += 1
        return ''.join(result)

    @staticmethod
    def _quote_iotdb_paths(sql: str) -> Tuple[str, List[str]]:
        pattern = re.compile(
            r"(root(?:\.(?:[\w\*]+|`[^`]+`|\"[^\"]+\"|'[^']+'))+)"
        )
        result = []
        last_end = 0
        quoted: List[str] = []
        for match in pattern.finditer(sql):
            start, end = match.span()
            if start > 0 and sql[start - 1] in "'\"`":
                continue
            path = match.group(1)
            if (
                    "*" in path
                    or re.search(r"\.[0-9]", path)
                    or any(q in path for q in ("`", "'", '"'))
            ):
                result.append(sql[last_end:start])
                result.append(f"'{path}'")
                quoted.append(path)
                last_end = end
        result.append(sql[last_end:])
        return "".join(result), quoted

    def _restore_iotdb_paths(self, sql: str) -> str:
        if not self._iotdb_paths:
            return sql
        for path in self._iotdb_paths:
            sql = sql.replace(f'"{path}"', path)
            sql = sql.replace(f"'{path}'", path)
            sql = sql.replace(f'`{path}`', path)
        return sql
