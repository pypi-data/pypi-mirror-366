from __future__ import annotations

import re
from multiprocessing.spawn import prepare
from types import ModuleType
from typing import List, cast, Dict, Any

import gpudb.dbapi

import sqlalchemy
from sqlalchemy import (
    exc,
    quoted_name,
    sql,
    util,
    types,
    Select,
    UnaryExpression,
    Connection, Over, BinaryExpression,
)
from sqlalchemy import types as sqltypes
from sqlalchemy.engine import default, reflection
from sqlalchemy.engine.interfaces import (
    ReflectedColumn,
    ReflectedForeignKeyConstraint,
    ReflectedIndex,
    ReflectedTableComment, IsolationLevel, DBAPIConnection,
)
from sqlalchemy.engine.reflection import cache
from sqlalchemy.exc import CompileError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import (
    compiler,
    functions,
)
from sqlalchemy.sql.compiler import SQLCompiler
from sqlalchemy.sql.ddl import DropConstraint, CreateColumn
from sqlalchemy.sql.schema import (
    ColumnCollectionConstraint,
    PrimaryKeyConstraint,
    Identity,
)
from sqlalchemy.testing.provision import update_db_opts
from typing_extensions import Literal

from sqlalchemy_kinetica import kinetica_types
from sqlalchemy_kinetica.kinetica_types import JSON

colspecs = {
    sqltypes.Date: kinetica_types.DATE,
    sqltypes.DateTime: kinetica_types.DATETIME,
    sqltypes.JSON: kinetica_types.JSON,
    sqltypes.Time: kinetica_types.TIME,
    sqltypes.DECIMAL: kinetica_types.VARCHAR
}

ischema_names = {
    "BIGINT": sqltypes.BIGINT,
    "BLOB": sqltypes.BLOB,
    "BOOL": sqltypes.BOOLEAN,
    "BOOLEAN": sqltypes.BOOLEAN,
    "CHAR": sqltypes.CHAR,
    "DATE": sqltypes.DATE,
    "DATE_CHAR": sqltypes.DATE,
    "DATETIME": sqltypes.DATETIME,
    "DATETIME_CHAR": sqltypes.DATETIME,
    "DOUBLE": sqltypes.DOUBLE,
    "DECIMAL": sqltypes.DECIMAL,
    "FLOAT": sqltypes.FLOAT,
    "INT": sqltypes.INTEGER,
    "INTEGER": sqltypes.INTEGER,
    "JSON": JSON,
    "NUMERIC": sqltypes.NUMERIC,
    "REAL": sqltypes.REAL,
    "SMALLINT": sqltypes.SMALLINT,
    "TEXT": sqltypes.TEXT,
    "TIME": sqltypes.TIME,
    "TIME_CHAR": sqltypes.TIME,
    "TIMESTAMP": sqltypes.TIMESTAMP,
    "VARCHAR": sqltypes.VARCHAR,
    "NVARCHAR": sqltypes.NVARCHAR,
    "NCHAR": sqltypes.NCHAR,
}

KI_INSERT_HINT_KEY = 'kinetica_insert_hint'
KI_PARTITION_CLAUSE_KEY = "kinetica_partition_clause"
KI_TIER_STRATEGY_KEY = "kinetica_tier_strategy"
KI_INDEX_KEY = "kinetica_index"
KI_CHUNK_SKIP_INDEX_KEY = "kinetica_chunk_skip_index"
KI_GEOSPATIAL_INDEX_KEY = "kinetica_geospatial_index"
KI_CAGRA_INDEX_KEY = "kinetica_cagra_index"
KI_EXTERNAL_TABLE_REMOTE_QUERY = 'kinetica_external_table_remote_query'
KI_EXTERNAL_TABLE_FILE_PATHS = 'kinetica_external_table_file_paths'
KI_EXTERNAL_TABLE_OPTION = 'kinetica_external_table_option'


class KineticaSqlCompiler(compiler.SQLCompiler):

    def limit_clause(self, select: Select[Any], **kw: Any) -> str:
        text = ""
        if select._limit_clause is not None:
            text += "\n LIMIT " + self.process(select._limit_clause, **kw)
        if select._offset_clause is not None:
            if select._limit_clause is None:
                # 2147384648 is the max. no. of records per result set
                # we can hardcode the value, because using a limit would lead to another cache key
                text += "\n LIMIT 2147384648"
            text += " OFFSET " + self.process(select._offset_clause, **kw)
        return text

    def visit_is_true_unary_operator(
            self, element: UnaryExpression[Any], operator: Any, **kw: Any
    ) -> str:
        return f"{self.process(element.element, **kw)} = TRUE"

    def visit_is_false_unary_operator(
            self, element: UnaryExpression[Any], operator: Any, **kw: Any
    ) -> str:
        return f"{self.process(element.element, **kw)} = FALSE"

    def visit_now_func(self, fn: functions.now, **kw: Any) -> str:
        return "CURRENT_TIMESTAMP"

    def visit_insert(self, insert_stmt, **kwargs):
        # Extract custom text from the insert statement's kwarg
        insert_hint = insert_stmt.kwargs.get('kinetica_insert_hint', '')
        insert_hint = f" /* {insert_hint} */" if insert_hint else ''

        # Get the base INSERT INTO clause
        insert_into = "INSERT INTO"

        # Get the table name formatted correctly for SQL
        table_name = self.preparer.format_table(insert_stmt.table)

        # Build the custom clause
        insert_clause = f"{insert_into} {table_name}{insert_hint}"

        # Generate the rest of the INSERT statement using the base method
        rest_of_the_query = super().visit_insert(insert_stmt, **kwargs)

        # Replace the standard INSERT INTO clause with our custom one
        return rest_of_the_query.replace(f"INSERT INTO {table_name}", insert_clause, 1)

    def visit_first_value(self, func, **kw):
        # Process the main column argument
        expr = self.process(func.clauses.clauses[0], **kw)

        # Determine whether to include the IGNORE NULLS or RESPECT NULLS clause
        nulls_clause = "IGNORE NULLS" if func.ignore_nulls else "RESPECT NULLS"

        return f"FIRST_VALUE({expr}) {nulls_clause}"

    def visit_update(self, update_stmt, **kw):

        has_join = hasattr(update_stmt, '_join_condition') and update_stmt._join_condition is not None
        has_where = hasattr(update_stmt, '_where_condition') and update_stmt._where_condition is not None

        if has_join and has_where :
            raise CompileError("Cannot have both 'join_condition' and 'where_condition' ")

        # Basic UPDATE clause
        update_sql = super().visit_update(update_stmt, **kw)

        # FROM clause with JOIN
        if has_join:
            if hasattr(update_stmt, '_from_table') and update_stmt._from_table is not None:
                from_clause = f"\nFROM {self.process(update_stmt.table, asfrom=True)}"
                if isinstance(update_stmt._join_condition, BinaryExpression):
                    from_clause += f"\nJOIN {self.process(update_stmt._from_table, asfrom=True)} ON {self.process(update_stmt._join_condition)}"
                update_sql += from_clause

            return update_sql
        elif has_where:
            from_clause = f"\nFROM {self.process(update_stmt.table, asfrom=True)}, {self.process(update_stmt._from_table, asfrom=True)}"
            from_clause += f"\nWHERE {self.process(update_stmt._where_condition)}"
            update_sql += from_clause
            return update_sql

        return update_sql

    def update_from_clause(self, update_stmt, from_table, extra_froms, from_hints, **kw):
        """
        Override the update_from_clause method to generate the desired SQL.
        This method will be used to construct the FROM clause in UPDATE statements.
        """
        # Generate the "FROM" clause manually

        return None


class KineticaDDLCompiler(compiler.DDLCompiler, SQLCompiler):

    def visit_create_table(self, create, **kwargs):

        def build_table_properties(d):
            # Create a list of formatted key-value pairs
            items = [f"{key} = {value}" for key, value in d.items()]

            # Join the items with commas
            items_string = ", ".join(items)

            # Enclose the string within parentheses
            result = f"({items_string})"

            return result

        table = create.element
        preparer = self.preparer

        # Start creating the CREATE TABLE statement
        text = "CREATE " + " ".join(table._prefixes + ['']) + "TABLE "
        text += preparer.format_table(table)

        # Process the columns list if given, in case of external tables
        # the column list might be absent.
        if len(table.columns) > 0:
            text += "\n("

            # Add the column definitions
            separator = "\n"
            pk_list = []
            sk_list = []
            for column in table.columns:
                text += separator
                separator = ",\n"

                col_def = self.get_column_specification(column)

                # If any column property is a shard key marker, add the col to the SK list;
                # otherwise, add the column property before the end paren, if exists;
                # otherwise, add it before [NOT] NULL, if exists; otherwise, add at end
                for col_prop in column.info:
                    col_prop = col_prop.upper()
                    if col_prop == "SHARD_KEY":
                        sk_list.append(column.name)
                    elif ")" in col_def:
                        col_def = f", {col_prop})".join(col_def.split(")"))
                    elif col_def.endswith("NOT NULL"):
                        col_def = f"{col_def[:-9]}({col_prop}) NOT NULL"
                    elif col_def.endswith("NULL"):
                        col_def = f"{col_def[:-5]}({col_prop}) NULL"
                    else:
                        col_def = f"{col_def}({col_prop})"

                if column.primary_key:
                    pk_list.append(column.name)

                text += "\t" + col_def

            # Add primary keys if any
            if len(pk_list) > 0:
                text += f",\n\tPRIMARY KEY ({', '.join(pk_list)})"

            # Add shard keys if any
            if len(sk_list) > 0:
                text += f",\n\tSHARD KEY ({', '.join(sk_list)})"

            text += "\n)\n"
        else:
            text += "\n"

        # Do special handling needed for EXTERNAL TABLE creation
        if any('EXTERNAL' == s.upper() for s in table._prefixes):
            remote_query = table.kwargs.get(KI_EXTERNAL_TABLE_REMOTE_QUERY, None)
            file_paths = table.kwargs.get(KI_EXTERNAL_TABLE_FILE_PATHS, None)

            if remote_query and len(remote_query) > 0 and file_paths and len(file_paths) > 0:
                raise CompileError(f"Both '{KI_EXTERNAL_TABLE_REMOTE_QUERY}' and '{KI_EXTERNAL_TABLE_FILE_PATHS}' "
                                   f"cannot be supplied, please use one ...")

            if remote_query and not isinstance(remote_query, str):
                raise CompileError(f"'{KI_EXTERNAL_TABLE_REMOTE_QUERY}' must be of type 'str'")
            if file_paths and not isinstance(file_paths, str):
                raise CompileError(f"'{KI_EXTERNAL_TABLE_FILE_PATHS}' must be of type 'str'")

            if remote_query and len(remote_query) > 0:
                text += f"REMOTE QUERY '{remote_query}'\n"

            if file_paths and len(file_paths) > 0:
                text += f"FILE PATHS '{file_paths}'\n"

            external_table_options = table.kwargs.get(KI_EXTERNAL_TABLE_OPTION, None)
            if external_table_options and not isinstance(external_table_options, dict):
                raise CompileError(f"'{external_table_options}' must be of type 'dict'")

            options = ', '.join(f"{k} = '{v}'" for k, v in external_table_options.items()) \
                if external_table_options else None

            text += f"WITH OPTIONS ({options})\n" if options else ""
        # END special handling needed for EXTERNAL TABLE creation

        # process partitions, tier strategy, indices and table properties in that order
        partition_clause = table.kwargs.get(KI_PARTITION_CLAUSE_KEY)
        if partition_clause and len(partition_clause) > 0:
            text += f"{partition_clause.strip()}\n"

        tier_strategy = table.kwargs.get(KI_TIER_STRATEGY_KEY)
        if tier_strategy and len(tier_strategy) > 0:
            text += f"TIER STRATEGY\n(\n\t{tier_strategy.strip()}\n)\n"

        # process normal index
        index_clause = ""
        index_info = table.kwargs.get(KI_INDEX_KEY)  # returns a list of lists of column names
        if index_info and not KineticaDialect._is_list_of_lists(index_info):
            raise CompileError(f"{KI_INDEX_KEY} must be a 'list of list/s'")
        if index_info and len(index_info) > 0:
            for index in index_info:
                index_clause += f"INDEX ({', '.join(index)})\n"
        if len(index_clause) > 0:
            text += index_clause

        # process chunk skip index
        chunk_skip_index_clause = ""
        chunk_skip_index_info = table.kwargs.get(KI_CHUNK_SKIP_INDEX_KEY)  # returns a column name
        if chunk_skip_index_info and not isinstance(chunk_skip_index_info, str):
            raise CompileError(f"{KI_CHUNK_SKIP_INDEX_KEY} must be a 'string'")
        if chunk_skip_index_info and len(chunk_skip_index_info) > 0:
            chunk_skip_index_clause += f"CHUNK SKIP INDEX ({chunk_skip_index_info})\n"
        if len(chunk_skip_index_clause) > 0:
            text += chunk_skip_index_clause

        # process geospatial index
        geospatial_index_clause = ""
        geospatial_index_info = table.kwargs.get(KI_GEOSPATIAL_INDEX_KEY)  # returns a list of column names
        if geospatial_index_info and not KineticaDialect._is_list_of_lists(geospatial_index_info):
            raise CompileError(f"{KI_GEOSPATIAL_INDEX_KEY} must be a 'list of list/s'")
        if geospatial_index_info and len(geospatial_index_info) > 0:
            for index in geospatial_index_info:
                geospatial_index_clause += f"GEOSPATIAL INDEX ({', '.join(index)})\n"
        if len(geospatial_index_clause) > 0:
            text += geospatial_index_clause

        # process cagra index
        cagra_index_info = table.kwargs.get(KI_CAGRA_INDEX_KEY)  # returns a list of index parameters
        if cagra_index_info:
            if not KineticaDialect._correct_cagra_index_structure(cagra_index_info):
                raise CompileError(f"{KI_CAGRA_INDEX_KEY} must be a list of a column name and optional options dict: '[<column_name>, <options_dict>]'")
            cagra_index_column = cagra_index_info[0]
            cagra_index_options = KineticaDialect._convert_cagra_options_dict_to_string(cagra_index_info[1]) if len(cagra_index_info) == 2 else None
            if not cagra_index_column or len(cagra_index_column.strip()) == 0:
                raise CompileError("Valid index column name not found")
            cagra_index_clause = f"CAGRA INDEX ({cagra_index_column})"
            if cagra_index_options and len(cagra_index_options) > 0:
                cagra_index_clause += f" WITH OPTIONS (INDEX_OPTIONS = '{cagra_index_options}')"
            text += cagra_index_clause + "\n"

        # process table properties
        table_properties = table.info

        if table_properties:
            text += f"USING TABLE PROPERTIES {build_table_properties(table_properties)}"

        return text.strip()



class KineticaTypeCompiler(compiler.GenericTypeCompiler):
    def visit_NUMERIC(self, type_: types.TypeEngine[Any], **kw: Any) -> str:
        return self.visit_DECIMAL(type_)

    def visit_TINYINT(self, type_: types.TypeEngine[Any], **kw: Any) -> str:
        return "TINYINT"

    def visit_string(self, type_: types.TypeEngine[Any], **kw: Any) -> str:
        # Normally string renders as VARCHAR, but we want NVARCHAR
        return self.visit_NVARCHAR(type_, **kw)

    def visit_unicode(self, type_: types.TypeEngine[Any], **kw: Any) -> str:
        # Normally unicode renders as VARCHAR, but we want NVARCHAR
        return self.visit_NVARCHAR(type_, **kw)

    def visit_TEXT(self, type_: types.TypeEngine[Any], **kw: Any) -> str:
        # Normally unicode renders as TEXT, but we want NCLOB
        return self.visit_NCLOB(type_, **kw)

    def visit_boolean(self, type_: types.TypeEngine[Any], **kw: Any) -> str:
        # Check if we want native or non-native booleans
        if self.dialect.supports_native_boolean:
            return self.visit_BOOLEAN(type_)
        return self.visit_TINYINT(type_)

    def visit_BINARY(self, type_: types.TypeEngine[Any], **kw: Any) -> str:
        return super().visit_VARBINARY(type_, **kw)

    def visit_DOUBLE_PRECISION(self, type_: types.TypeEngine[Any], **kw: Any) -> str:
        return super().visit_DOUBLE(type_, **kw)

    def visit_uuid(self, type_: types.TypeEngine[Any], **kw: Any) -> str:
        return self._render_string_type(type_, "NVARCHAR", length_override=32)

    def visit_JSON(self, type_: types.TypeEngine[Any], **kw: Any) -> str:
        return "JSON"

    def visit_NVARCHAR(self, type_, **kw):
        return self._render_string_type(type_, "VARCHAR")


class KineticaIdentifierPreparer(compiler.IdentifierPreparer):
    reserved_words = {
        "abs",
        "access",
        "all",
        "allocate",
        "allow",
        "alter",
        "and",
        "any",
        "are",
        "array",
        "array_max_cardinality",
        "as",
        "asensitive",
        "asof",
        "asymmetric",
        "atomic",
        "authorization",
        "avg",
        "begin",
        "begin_frame",
        "begin_partition",
        "between",
        "bigint",
        "binary",
        "bit",
        "blob",
        "boolean",
        "both",
        "bucket",
        "by",
        "bytes",
        "call",
        "called",
        "cardinality",
        "cascaded",
        "case",
        "cast",
        "ceil",
        "ceiling",
        "char_length",
        "character",
        "character_length",
        "check",
        "classifier",
        "clob",
        "close",
        "coalesce",
        "collate",
        "collect",
        "collection",
        "column",
        "commit",
        "compression",
        "condition",
        "connect",
        "constraint",
        "convert",
        "copy",
        "corr",
        "corresponding",
        "covar_pop",
        "covar_samp",
        "create",
        "cross",
        "cube",
        "cume_dist",
        "current",
        "current_catalog",
        "current_date",
        "current_default_transform_group",
        "current_path",
        "current_role",
        "current_row",
        "current_schema",
        "current_time",
        "current_timestamp",
        "current_transform_group_for_type",
        "current_user",
        "cursor",
        "cycle",
        "deallocate",
        "dec",
        "declare",
        "default_",
        "defaultvalue",
        "define",
        "delete",
        "delimited",
        "dense_rank",
        "deref",
        "describe",
        "deterministic",
        "dict",
        "disallow",
        "disconnect",
        "disk_optimized",
        "distinct",
        "drop",
        "dynamic",
        "each",
        "element",
        "else",
        "empty",
        "end",
        "end_exec",
        "end_frame",
        "end_partition",
        "equals",
        "escape",
        "every",
        "except",
        "exec",
        "execute",
        "exists",
        "exp",
        "explain",
        "extend",
        "external",
        "extract",
        "false",
        "fetch",
        "first_value",
        "floor",
        "for",
        "foreign",
        "format",
        "frame_row",
        "free",
        "from",
        "full",
        "function",
        "fusion",
        "get",
        "global",
        "grant",
        "group",
        "grouping",
        "groups",
        "having",
        "hold",
        "identified",
        "identity",
        "ignore",
        "import",
        "in",
        "include",
        "indicator",
        "initial",
        "inner",
        "inout",
        "insensitive",
        "insert",
        "integer",
        "intersect",
        "intersection",
        "interval",
        "into",
        "is",
        "join",
        "json_array",
        "json_arrayagg",
        "json_exists",
        "json_object",
        "json_objectagg",
        "json_query",
        "json_value",
        "kerberos",
        "lag",
        "language",
        "large",
        "last_value",
        "lateral",
        "lead",
        "leading",
        "left",
        "like",
        "like_regex",
        "limit",
        "ln",
        "local",
        "localtime",
        "localtimestamp",
        "lower",
        "match",
        "match_number",
        "match_recognize",
        "max",
        "measures",
        "member",
        "merge",
        "method",
        "min",
        "minus",
        "mod",
        "modifies",
        "modify",
        "module",
        "move",
        "multiset",
        "national",
        "natural",
        "nchar",
        "nclob",
        "new",
        "next",
        "no",
        "none",
        "normalize",
        "not",
        "nth_value",
        "ntile",
        "null",
        "nullif",
        "numeric",
        "occurrences_regex",
        "octet_length",
        "of",
        "offset",
        "old",
        "omit",
        "on",
        "one",
        "only",
        "open",
        "or",
        "order",
        "out",
        "outer",
        "over",
        "overlaps",
        "overlay",
        "parameter",
        "partition",
        "password",
        "paths",
        "pattern",
        "per",
        "percent",
        "percent_rank",
        "percentile_cont",
        "percentile_disc",
        "period",
        "permute",
        "pivot",
        "portion",
        "position_regex",
        "power",
        "precedes",
        "precision",
        "prepare",
        "prev",
        "primary",
        "primary_key",
        "procedure",
        "protected",
        "quote_",
        "range",
        "rank",
        "reads",
        "real",
        "recursive",
        "references",
        "referencing",
        "regr_avgx",
        "regr_avgy",
        "regr_count",
        "regr_intercept",
        "regr_r2",
        "regr_slope",
        "regr_sxx",
        "regr_sxy",
        "regr_syy",
        "release",
        "rename",
        "replicated",
        "reset",
        "resource_",
        "respect",
        "result",
        "return",
        "revoke",
        "right",
        "rollback",
        "rollup",
        "row",
        "row_number",
        "rows",
        "running",
        "savepoint",
        "scope",
        "scroll",
        "search",
        "seconds",
        "seek",
        "select",
        "sensitive",
        "session_user",
        "set",
        "set_minus",
        "shard",
        "shard_key",
        "show",
        "similar",
        "skip_",
        "smallint",
        "some",
        "specific",
        "specifictype",
        "sql",
        "sql_datetime",
        "sql_tsi_millisecond",
        "sqlexception",
        "sqlstate",
        "sqlwarning",
        "sqrt",
        "start",
        "static",
        "statistics",
        "stddev_pop",
        "stddev_samp",
        "stream",
        "submultiset",
        "subset",
        "substr",
        "substring",
        "substring_regex",
        "succeeds",
        "sum",
        "symmetric",
        "system_time",
        "system_user",
        "table",
        "tablesample",
        "text_search",
        "then",
        "timezone_hour",
        "timezone_minute",
        "tinyint",
        "to",
        "token_",
        "top",
        "trailing",
        "translate",
        "translate_regex",
        "translation",
        "treat",
        "trigger",
        "trim",
        "trim_array",
        "true",
        "truncate",
        "ttl",
        "uescape",
        "union",
        "unique",
        "unknown",
        "unnest",
        "unpivot",
        "unsigned",
        "update",
        "upper",
        "upsert",
        "user",
        "using",
        "value_of",
        "values",
        "var_pop",
        "var_samp",
        "varbinary",
        "varchar",
        "varying",
        "versioning",
        "when",
        "whenever",
        "where",
        "width_bucket",
        "window",
        "with",
        "within",
        "without",
    }


# class KineticaExecutionContext(default.DefaultExecutionContext):
#     @util.memoized_property
#     def _preserve_raw_colnames(self):
#         return not self.dialect._broken_dotted_colnames or self.execution_options.get(
#             "sqlite_raw_colnames", False
#         )
#
#     def _translate_colname(self, colname):
#         # TODO: detect SQLite version 3.10.0 or greater;
#         # see [ticket:3633]
#
#         # adjust for dotted column names.  SQLite
#         # in the case of UNION may store col names as
#         # "tablename.colname", or if using an attached database,
#         # "database.tablename.colname", in cursor.description
#         if not self._preserve_raw_colnames and "." in colname:
#             return colname.split(".")[-1], colname
#         else:
#             return colname, None


class KineticaDialect(default.DefaultDialect):
    returns_native_bytes = True

    name = "kinetica"
    supports_alter = False

    # SQlite supports "DEFAULT VALUES" but *does not* support
    # "VALUES (DEFAULT)"
    supports_default_values = False
    supports_default_metavalue = False

    # sqlite issue:
    # https://github.com/python/cpython/issues/93421
    # note this parameter is no longer used by the ORM or default dialect
    # see #9414
    supports_sane_rowcount_returning = False

    supports_empty_insert = False
    supports_native_boolean = True
    supports_cast = True
    supports_multivalues_insert = True
    use_insertmanyvalues = True
    tuple_in_values = True
    supports_statement_cache = True
    insert_null_pk_still_autoincrements = True
    insert_returning = False
    update_returning = False
    update_returning_multifrom = False
    delete_returning = False
    update_returning_multifrom = False
    cte_follows_insert = True

    supports_default_metavalue = False
    """dialect supports INSERT... VALUES (DEFAULT) syntax"""

    default_metavalue_token = ""
    """for INSERT... VALUES (DEFAULT) syntax, the token to put in the
    parenthesis."""

    default_paramstyle = "qmark"
    default_isolation_level = 'AUTOCOMMIT'
    # execution_ctx_cls = KineticaExecutionContext
    statement_compiler = KineticaSqlCompiler
    ddl_compiler = KineticaDDLCompiler
    type_compiler_cls = KineticaTypeCompiler
    preparer = KineticaIdentifierPreparer
    ischema_names = ischema_names
    colspecs = colspecs

    _broken_fk_pragma_quotes = False
    _broken_dotted_colnames = False
    default_schema_name: str = None  # this is always set for us

    types_with_length = [
        kinetica_types.CHARACTER,
        kinetica_types.NUMERIC,
    ]

    @classmethod
    def import_dbapi(cls) -> ModuleType:
        gpudb.dbapi.paramstyle = cls.default_paramstyle  # type:ignore[assignment]
        return gpudb.dbapi

    if sqlalchemy.__version__ < "2":  # pragma: no cover
        dbapi = import_dbapi  # type:ignore[assignment]

    def __init__(
            self,
            native_datetime=False,
            json_serializer=None,
            json_deserializer=None,
            **kwargs,
    ):
        default.DefaultDialect.__init__(self, **kwargs)

        self._json_serializer = json_serializer
        self._json_deserializer = json_deserializer

        # this flag used by pysqlite dialect, and perhaps others in the
        # future, to indicate the driver is handling date/timestamp
        # conversions (and perhaps datetime/time as well on some hypothetical
        # driver ?)
        self.native_datetime = native_datetime

    @classmethod
    def get_dialect(cls):
        return cls

    def do_begin(self, dbapi_connection):
        # Disable automatic transactions by overriding the `do_begin` method to do nothing
        pass

    def do_commit(self, dbapi_connection):
        # Disable commits
        pass

    def do_rollback(self, dbapi_connection):
        # Disable rollback
        pass

    def get_default_isolation_level(self, dbapi_conn):
        return self.default_isolation_level

    def get_isolation_level_values(self, dbapi_conn: DBAPIConnection)-> List[IsolationLevel]:
        return Literal["AUTOCOMMIT"]

    def normalize_name(self, name: str) -> str:
        if not name:
            return name

        if name.upper() == name and not self.identifier_preparer._requires_quotes(
                name.lower()
        ):
            name = name.lower()
        elif name.lower() == name:
            return quoted_name(name, quote=True)

        return name

    def denormalize_name(self, name: str) -> str:
        if not name:
            return name

        if name.lower() == name and not self.identifier_preparer._requires_quotes(
                name.lower()
        ):
            name = name.upper()
        return name

    @reflection.cache
    def get_schema_names(self, connection, **kw):
        result = connection.execute(
            sql.text("SELECT schema_name FROM ki_catalog.ki_schemas ")
        )

        if result.rowcount == 0:
            return []

        schema_names = list(self.normalize_name(row[0]) for row in result.fetchall())
        return schema_names

    def _format_schema(self, schema, table_name):
        if schema is not None:
            qschema = self.identifier_preparer.quote_identifier(schema)
            name = f"{qschema}.{table_name}"
        else:
            name = table_name
        return name

    @reflection.cache
    def get_table_names(self, connection, schema=None, sqlite_include_internal=False, **kw):

        schema_name = schema or self.get_default_schema_name(connection)

        result = connection.execute(
            sql.text(
                """
                    SELECT object_name
                    FROM ki_catalog.ki_objects
                    WHERE obj_kind IN ('E', 'H', 'R')
                    AND UPPER(schema_name) = :schema
                """
            ).bindparams(schema = schema_name.upper())
        )

        if result.rowcount == 0:
            return []

        table_names = list(self.normalize_name(row[0]) for row in result.fetchall())
        return table_names

    @reflection.cache
    def get_temp_table_names(self, connection, schema=None, sqlite_include_internal=False, **kw):

        schema_name = schema or self.get_default_schema_name(connection)

        result = connection.execute(
            sql.text(
                """
                    SELECT object_name
                    FROM ki_catalog.ki_objects
                    WHERE obj_kind IN ('E', 'H', 'R')
                    AND persistence = 'T'
                    AND UPPER(schema_name) = :schema
                """
            ).bindparams(schema = schema_name.upper())
        )

        if result.rowcount == 0:
            return []

        table_names = list(self.normalize_name(row[0]) for row in result.fetchall())
        return table_names

    @reflection.cache
    def get_temp_view_names(self, connection, schema=None, sqlite_include_internal=False, **kw):

        schema_name = schema or self.get_default_schema_name(connection)

        result = connection.execute(
            sql.text(
                """
                    SELECT object_name
                    FROM ki_catalog.ki_objects
                    WHERE obj_kind IN ('I', 'M', 'V')
                    AND persistence = 'T'
                    AND UPPER(schema_name) = :schema
                """
            ).bindparams(schema = schema_name.upper())
        )

        if result.rowcount == 0:
            return []

        view_names = list(self.normalize_name(row[0]) for row in result.all())
        return view_names

    @reflection.cache
    def has_table(self, connection, table_name, schema=None, **kw):

        schema_name = schema or self.get_default_schema_name(connection)

        result = connection.execute(
            sql.text(
                """
                    SELECT 1
                    FROM ki_catalog.ki_objects
                    WHERE obj_kind IN ('E', 'H', 'I', 'M', 'R', 'V')
                    AND UPPER(schema_name) = :schema AND UPPER(object_name) = :table
                """
            ).bindparams(
                schema = schema_name.upper(),
                table = table_name.upper(),
            )
        )

        return result.rowcount == 1

    def get_default_schema_name(self, connection):

        if not self.default_schema_name:

            result = connection.execute(
                sql.text(
                    """
                        SELECT CURRENT_SCHEMA()
                    """
                )
            )
    
            self.default_schema_name = result.first()[0]

        return self.default_schema_name

    @reflection.cache
    def get_view_names(self, connection, schema=None, sqlite_include_internal=False, **kw):

        schema_name = schema or self.get_default_schema_name(connection)

        result = connection.execute(
            sql.text(
                """
                    SELECT object_name
                    FROM ki_catalog.ki_objects
                    WHERE obj_kind IN ('V')
                    AND UPPER(schema_name) = :schema
                """
            ).bindparams(schema = schema_name.upper())
        )

        if result.rowcount == 0:
            return []

        tables = list(self.normalize_name(row[0]) for row in result.fetchall())
        return tables

    @reflection.cache
    def get_materialized_view_names(self, connection, schema=None, sqlite_include_internal=False, **kw):

        schema_name = schema or self.get_default_schema_name(connection)

        result = connection.execute(
            sql.text(
                """
                    SELECT object_name
                    FROM ki_catalog.ki_objects
                    WHERE obj_kind IN ('M')
                    AND UPPER(schema_name) = :schema
                """
            ).bindparams(schema = schema_name.upper())
        )

        if result.rowcount == 0:
            return []

        tables = list(self.normalize_name(row[0]) for row in result.fetchall())
        return tables

    @reflection.cache
    def get_view_definition(self, connection, view_name, schema=None, **kw):

        schema_name = schema or self.get_default_schema_name(connection)

        result = connection.execute(
            sql.text(
                """
                    SELECT definition
                    FROM ki_catalog.ki_objects
                    WHERE obj_kind IN ('M', 'V')
                    AND UPPER(schema_name) = :schema AND UPPER(object_name) = :view_name
                    LIMIT 1
                """
            ).bindparams(
                schema = schema_name.upper(),
                view_name = view_name.upper(),
            )
        )

        if result.rowcount == 0:
            return None
        return result.scalar()

    @staticmethod
    def _is_list_of_lists(variable):
        if isinstance(variable, list) and all(isinstance(item, list) for item in variable):
            return True
        return False


    @staticmethod
    def _correct_cagra_index_structure(lst):
        # Check if the list has one or two elements
        if not lst or not isinstance(lst, list):
            return False
        if len(lst) == 1:
            # Check if the first element is a string
            return isinstance(lst[0], str)
        if len(lst) == 2:
            # Check if the first element is a string and the second element is a dictionary
            return isinstance(lst[0], str) and isinstance(lst[1], dict)
        return False


    @staticmethod
    def _convert_cagra_options_dict_to_string(d):
        # Join each key-value pair as 'key: value' and then join them with ', ' in between
        return ', '.join(f'{key}: {value}' for key, value in d.items())


    @staticmethod
    def _type_has_size(input_string):
        # Regex pattern to match "(<some_number>)" or "(<some_number>, <some_number>)"
        pattern = r"\(\d+(, \d+)?\)"

        # Use re.search to check if the pattern is present in the string
        match = re.search(pattern, input_string)

        return bool(match)


    @staticmethod
    def _extract_type_before_size(input_string):
        # Use regex to match the pattern and capture the string before the parenthesis
        match = re.match(r"^([^\(]+)\(", input_string)
        if match:
            return match.group(1)
        return None


    @cache
    def get_columns(self, connection, table_name, schema=None, **kw) -> List[ReflectedColumn]:

        schema_name = schema or self.get_default_schema_name(connection)

        result = connection.execute(
            sql.text(
                """
                    SELECT
                        c.column_name,
                        t.name,
                        t.sql_typename,
                        c.default_value,
                        c.is_nullable, 
                        IF(t.sql_typename = 'vector', INT(SUBSTRING(c.properties, 8, POSITION(')' IN c.properties)-8)), t.size) size, 
                        scale,
                        c.properties,
                        c.comments
                    FROM ki_catalog.ki_columns c 
                    JOIN ki_catalog.ki_datatypes t ON c.column_type_oid = t.oid 
                    WHERE UPPER(c.schema_name) = :schema AND UPPER(c.table_name) = :table
                    ORDER BY c.column_position
                """
            ).bindparams(
                schema = schema_name.upper(),
                table = table_name.upper()
            )
        )

        if result.rowcount == 0:
            return None

        columns: List[ReflectedColumn] = []
        for row in result:
            column = {
                "name": self.normalize_name(row[0]),
                "default": row[2],
                "nullable": row[4] == 1,
                "size": row[5],
                "scale": row[6],
                "properties": row[7],
                "comment": row[8],
            }

            sql_type = None
            if KineticaDialect._type_has_size(str(row[2])):
                sql_type = KineticaDialect._extract_type_before_size(str(row[2])).capitalize()
            else:
                sql_type = str(row[2]).capitalize()

            if sql_type == "Double precision":
                sql_type = "DOUBLE_PRECISION"

            if sql_type == "Timestamp without time zone":
                sql_type = "TIMESTAMP"

            if hasattr(kinetica_types, sql_type):
                column["type"] = getattr(kinetica_types,sql_type)
            elif hasattr(types, sql_type):
                column["type"] = getattr(types, sql_type)
            else:
                if sql_type != "Numeric(18,4)":
                    util.warn(
                        f"Did not recognize type '{sql_type}' of column '{column['name']}'"
                    )
                column["type"] = types.NULLTYPE

            if column["type"] == kinetica_types.DECIMAL:
                column["type"] = kinetica_types.DECIMAL(row[5], row[6])
            elif column["type"] == kinetica_types.Numeric:
                column["type"] = kinetica_types.Numeric(row[5], row[6])
            elif column["type"] == kinetica_types.FLOAT:
                column["type"] = kinetica_types.FLOAT(row[5])
            elif column["type"] in [kinetica_types.Vector, kinetica_types.VECTOR, kinetica_types.vector]:
                column["type"] = kinetica_types.Vector(row[5])
            elif column["type"] in self.types_with_length:
                column["type"] = column["type"](row[5])

            columns.append(cast("ReflectedColumn", column))

        return columns

    @cache
    def get_table_oid(
            self,
            connection: Connection,
            table_name: str,
            schema: str | None = None,
            **kw: Any,
    ) -> int:

        schema_name = schema or self.get_default_schema_name(connection)

        result = connection.execute(
            sql.text(
                """
                    SELECT oid
                    FROM ki_catalog.ki_objects
                    WHERE obj_kind IN ('E', 'H', 'R', 'I', 'M', 'V')
                    AND UPPER(schema_name) = :schema AND UPPER(object_name) = :table
                """
            ).bindparams(
                schema = schema_name.upper(),
                table = table_name.upper(),
            )
        )

        if result.rowcount == 0:
            return None

        return cast(int, result.scalar())

    @cache
    def get_table_comment(
            self,
            connection: Connection,
            table_name: str,
            schema: str | None = None,
            **kw: Any,
    ) -> ReflectedTableComment:

        schema_name = schema or self.get_default_schema_name(connection)

        result = connection.execute(
            sql.text(
                """
                    SELECT comments
                    FROM ki_catalog.ki_objects
                    WHERE obj_kind IN ('E', 'H', 'R', 'I', 'M', 'V')
                    AND UPPER(schema_name) = :schema AND UPPER(object_name) = :table
                """
            ).bindparams(
                schema = schema_name.upper(),
                table = table_name.upper(),
            )
        )

        if result.rowcount == 0:
            return None

        return {"text": result.scalar()}

    @reflection.cache
    def get_pk_constraint(self, connection, table_name, schema=None, **kw):

        schema_name = schema or self.get_default_schema_name(connection)

        result = connection.execute(
            sql.text(
                """
                    SELECT oid, column_name
                    FROM ki_catalog.ki_columns
                    WHERE UPPER(schema_name) = :schema AND UPPER(table_name) = :table
                    AND is_primary_key = 1
                    ORDER BY column_position
                """
            ).bindparams(
                schema = schema_name.upper(),
                table = table_name.upper(),
            )
        )

        if result.rowcount == 0:
            return None

        constraint_name = None
        constrained_columns = []
        for row in result:
            constraint_name = str(row[0])
            constrained_columns.append(self.normalize_name(row[1]))

        return {
            "name": self.normalize_name(cast(str, constraint_name)),
            "constrained_columns": constrained_columns,
            "dialect_options": None
        }

    @reflection.cache
    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        # schema_name = schema or self.default_schema_name
        # if not self.has_table(connection, table_name, schema_name, **kw):
        #     raise exc.NoSuchTableError()
        #
        # result = connection.execute(
        #     sql.text(
        #         "SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_SCHEMA_NAME, "
        #         "REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME, UPDATE_RULE, DELETE_RULE "
        #         "FROM SYS.REFERENTIAL_CONSTRAINTS "
        #         "WHERE SCHEMA_NAME=:schema AND TABLE_NAME=:table "
        #         "ORDER BY CONSTRAINT_NAME, POSITION"
        #     ).bindparams(
        #         schema=self.denormalize_name(schema_name),
        #         table=self.denormalize_name(table_name),
        #     )
        # )
        # foreign_keys: dict[str, ReflectedForeignKeyConstraint] = {}
        # foreign_keys_list: list[ReflectedForeignKeyConstraint] = []
        #
        # for row in result:
        #     foreign_key_name = self.normalize_name(row[0])
        #
        #     if foreign_key_name in foreign_keys:
        #         foreign_key = foreign_keys[foreign_key_name]
        #         foreign_key["constrained_columns"].append(self.normalize_name(row[1]))
        #         foreign_key["referred_columns"].append(self.normalize_name(row[4]))
        #     else:
        #         foreign_key = {
        #             "name": foreign_key_name,
        #             "constrained_columns": [self.normalize_name(row[1])],
        #             "referred_schema": None,
        #             "referred_table": self.normalize_name(row[3]),
        #             "referred_columns": [self.normalize_name(row[4])],
        #             "options": {"onupdate": row[5], "ondelete": row[6]},
        #         }
        #
        #         if row[2] != self.denormalize_name(self.default_schema_name):
        #             foreign_key["referred_schema"] = self.normalize_name(row[2])
        #
        #         foreign_keys[foreign_key_name] = foreign_key
        #         foreign_keys_list.append(foreign_key)
        #
        # return sorted(
        #     foreign_keys_list,
        #     key=lambda foreign_key: (
        #         foreign_key["name"] is not None,
        #         foreign_key["name"],
        #     ),
        # )
        return []

    @reflection.cache
    def get_indexes(self, connection, table_name, schema=None, **kw):
    #     schema_name = schema or self.default_schema_name
    #     if not self.has_table(connection, table_name, schema_name, **kw):
    #         raise exc.NoSuchTableError()
    #
    #     result = connection.execute(
    #         sql.text(
    #             'SELECT "INDEX_NAME", "COLUMN_NAME", "CONSTRAINT" '
    #             "FROM SYS.INDEX_COLUMNS "
    #             "WHERE SCHEMA_NAME=:schema AND TABLE_NAME=:table "
    #             "ORDER BY POSITION"
    #         ).bindparams(
    #             schema=self.denormalize_name(schema_name),
    #             table=self.denormalize_name(table_name),
    #         )
    #     )
    #
    #     indexes: Dict[str, ReflectedIndex] = {}
    #     for name, column, constraint in result.fetchall():
    #         if constraint == "PRIMARY KEY":
    #             continue
    #
    #         if not name.startswith("_SYS"):
    #             name = self.normalize_name(name)
    #         column = self.normalize_name(column)
    #
    #         if name not in indexes:
    #             indexes[name] = {
    #                 "name": name,
    #                 "unique": False,
    #                 "column_names": [column],
    #             }
    #
    #             if constraint is not None:
    #                 indexes[name]["unique"] = "UNIQUE" in constraint.upper()
    #
    #         else:
    #             indexes[name]["column_names"].append(column)
    #
    #     return sorted(
    #         list(indexes.values()),
    #         key=lambda index: (index["name"] is not None, index["name"]),
    #     )
        return []