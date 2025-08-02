from os import readv
from random import randint

from sqlalchemy import Executable, ClauseElement, FunctionElement, literal_column, BinaryExpression, Select
from sqlalchemy.exc import CompileError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.dml import Insert, Update
from sqlalchemy.sql.functions import GenericFunction
from sqlparse.sql import Where

from sqlalchemy_kinetica.dialect import KI_INSERT_HINT_KEY

def quote_qualified_table_name(qualified_table_name):
    if not qualified_table_name:
        return None
    parts = qualified_table_name.split('.')
    quoted_parts = [f"\"{part}\"" for part in parts]
    return '.'.join(quoted_parts)

def safe_index(lst, value):
    return lst.index(value) if value in lst else len(lst)


class KiInsert(Insert):
    inherit_cache = False

    def __init__(self, *args, insert_hint=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Store kinetica insert hint in the kwargs to be accessed later by the compiler.
        self.kwargs[KI_INSERT_HINT_KEY] = insert_hint


@compiles(KiInsert, 'kinetica')
def compile_ki_insert(insert, compiler, **kwargs):
    return compiler.visit_insert(insert, **kwargs)


# Use the CustomInsert class in place of the regular insert
def ki_insert(table, insert_hint=None, **kwargs):
    return KiInsert(table, insert_hint=insert_hint, **kwargs)


class KiUpdate(Update):
    def __init__(self, table, from_table, join_condition=None, where_condition=None,  *args, **kwargs):
        super().__init__(table, *args, **kwargs)
        self._from_table = from_table
        self._join_condition = join_condition
        self._where_condition = where_condition

    @property
    def from_table(self):
        return self._from_table

    @property
    def join_condition(self):
        return self._join_condition

    @property
    def where_condition(self):
        return self._where_condition


@compiles(KiUpdate, 'kinetica')
def compile_ki_update(update, compiler, **kwargs):
    return compiler.visit_update(update, **kwargs)


class InsertFromSelect(Executable, ClauseElement):
    inherit_cache = False

    def __init__(self, table, select):
        self.table = table
        self.select = select


@compiles(InsertFromSelect, 'kinetica')
def visit_insert_from_select(element, compiler, **kw):
    return "INSERT INTO %s (%s)" % (
        compiler.process(element.table, **kw),
        compiler.process(element.select, **kw)
    )


class CreateTableAs(Executable, ClauseElement):
    inherit_cache = False

    def __init__(self, table, query, prefixes=None, table_properties= None):
        self.table = table
        self.query = query
        self.prefixes = prefixes
        self.table_properties = table_properties


@compiles(CreateTableAs, "kinetica")
def _create_table_as(element, compiler, **kw):

    def build_table_properties(d):

        if not d:
            return ""

        # Create a list of formatted key-value pairs
        items = [f"{key} = {value}" for key, value in d.items()]

        # Join the items with commas
        items_string = ", ".join(items)

        # Enclose the string within parentheses and add the UTP clause
        result = f"USING TABLE PROPERTIES ({items_string})"

        return result

    prefixes = " ".join(element.prefixes + ['']) if element.prefixes else ""
    props = build_table_properties(element.table_properties)
    return f"CREATE {prefixes}TABLE {element.table} AS\n{compiler.process(element.query)}\n{props}".strip()


# Define the custom function
class Asof(FunctionElement):
    inherit_cache = True
    name = 'asof'

# Compile the function into SQL
@compiles(Asof)
def compile_asof(element, compiler, **kwargs):
    left_column = compiler.process(element.clauses.clauses[0])
    right_column = compiler.process(element.clauses.clauses[1])
    rel_range_begin = compiler.process(element.clauses.clauses[2])
    rel_range_end = compiler.process(element.clauses.clauses[3])
    min_max = compiler.process(element.clauses.clauses[4])

    return f"ASOF({left_column}, {right_column}, {rel_range_begin}, {rel_range_end}, {min_max})"


class FirstValue(GenericFunction):
    inherit_cache = True
    name = 'first_value'

    def __init__(self, expr, ignore_nulls=True, **kwargs):
        super().__init__(expr, **kwargs)
        self.ignore_nulls = ignore_nulls


@compiles(FirstValue, "kinetica")
def compile_first_value(element, compiler, **kwargs):
    return compiler.visit_first_value(element, **kwargs)


class Pivot(ClauseElement):
    def __init__(self, value_agg_fn, type_column, type_values):
        self.value_agg_fn = value_agg_fn
        self.type_column = type_column
        self.type_values = type_values


# Extend the Select class to support PIVOT
class PivotSelect(Select):
    inherit_cache = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._source_alias = None
        self._pivot = None

    def select_from(self, pivot_source):
        self._source_alias = f"p_sq_{randint(0,1000000000)}"
        self = super().select_from(pivot_source.alias(self._source_alias))
        return self

    def pivot(self, value_agg_fn, type_column, type_values):
        self._pivot = Pivot(value_agg_fn, type_column, type_values)
        return self


# Custom compilation for Select that includes the PIVOT clause
@compiles(PivotSelect)
def compile_pivot_select(element, compiler, **kwargs):

    # Compile the inner select first
    query = compiler.visit_select(element, **kwargs)

    # If there's a pivot clause, inject it
    if element._pivot is not None:
        sq_alias_clause = f" AS {element._source_alias}"
        sq_alias_begin_index = safe_index(query, sq_alias_clause)
        sq_alias_end_index = sq_alias_begin_index + len(sq_alias_clause) + 1
        
        pivot_sql = (
            f"PIVOT ({element._pivot.value_agg_fn} "
            f"FOR {element._pivot.type_column} "
            f"IN ({', '.join(map(str, element._pivot.type_values))}))"
        )

        query = f"{query[:sq_alias_begin_index]}\n{pivot_sql}\n{query[sq_alias_end_index:]}"

    return query


# Custom UNPIVOT clause class
class Unpivot:
    def __init__(self, unpivoted_value_column, unpivoted_type_column, value_columns):
        self.unpivoted_value_column = unpivoted_value_column
        self.unpivoted_type_column = unpivoted_type_column
        self.value_columns = value_columns


# Extend the Select class to include the UNPIVOT clause
class UnpivotSelect(Select):
    inherit_cache = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._source_alias = None
        self._unpivot = None

    def select_from(self, unpivot_source):
        self._source_alias = f"up_sq_{randint(0,1000000000)}"
        self = super().select_from(unpivot_source.alias(self._source_alias))
        return self

    def unpivot(self, unpivoted_value_column, unpivoted_type_column, value_columns):
        self._unpivot = Unpivot(unpivoted_value_column, unpivoted_type_column, value_columns)
        return self


# Custom SQL compilation for the Unpivot clause
@compiles(UnpivotSelect)
def compile_unpivot_select(element, compiler, **kwargs):

    # Compile the inner select first
    query = compiler.visit_select(element, **kwargs)

    # If there's an unpivot clause, inject it
    if element._unpivot is not None:
        sq_alias_clause = f" AS {element._source_alias}"
        sq_alias_begin_index = safe_index(query, sq_alias_clause)
        sq_alias_end_index = sq_alias_begin_index + len(sq_alias_clause) + 1

        unpivot_sql = (
            f"UNPIVOT ({element._unpivot.unpivoted_value_column} "
            f"FOR {element._unpivot.unpivoted_type_column} "
            f"IN ({', '.join(element._unpivot.value_columns)}))"
        )

        query = f"{query[:sq_alias_begin_index]}\n{unpivot_sql}\n{query[sq_alias_end_index:]}"

    return query


class FilterByString(Executable, ClauseElement):
    def __init__(self, table_name, mode, expression, view_name = None, column_names = None, options = None):
        self.execution_mode = "EXECUTE" if view_name else "SELECT"
        self.table_name = table_name
        self.view_name = view_name
        self.column_names = column_names
        self.mode = mode
        if column_names and self.mode.upper() == "SEARCH":
            raise CompileError("'mode' 'search' and 'column_names' cannot be used together")
        self.expression = expression
        self.options = options or {}


# Custom SQL compiler for FilterByString
@compiles(FilterByString)
def compile_filter_by_string(element, compiler, **kw):
    table_name = compiler.process(element.table_name, **kw)
    mode = compiler.process(literal_column(element.mode), **kw)
    expression = compiler.process(literal_column(element.expression), **kw)

    table_name = table_name.replace("\n", "\n\t\t\t")

    parts = [
        "\tFILTER_BY_STRING\n\t(\n",
        f"\t\tTABLE_NAME => INPUT_TABLE\n\t\t(\n\t\t\t{table_name}\n\t\t)",
    ]

    if element.view_name is not None:
        parts.append(f",\n\t\tVIEW_NAME => '{element.view_name}'")

    if element.column_names is not None:
        parts.append(f",\n\t\tCOLUMN_NAMES => '{element.column_names}'")

    parts.append(f",\n\t\tMODE => '{mode}'")
    parts.append(f",\n\t\tEXPRESSION => '{expression}'")

    if element.options:
        options_str = ', '.join(
            f"'{k}' = '{v}'" for k, v in element.options.items()
        )
        parts.append(f",\n\t\tOPTIONS => KV_PAIRS({options_str})")

    parts.append("\n\t)\n")

    execution_mode_prefix = "SELECT *\nFROM TABLE\n(\n" if element.execution_mode == "SELECT" else "EXECUTE FUNCTION "

    return execution_mode_prefix + "".join(parts) + (")" if element.execution_mode == "SELECT" else "")


class EvaluateModel(Executable, ClauseElement):
    def __init__(self, model, deployment_mode, replications, source_table, destination_table = None):
        self.execution_mode = "EXECUTE" if destination_table else "SELECT"
        self.model = model
        self.deployment_mode = deployment_mode
        self.replications = replications
        self.source_table = source_table
        self.destination_table = destination_table


# Custom SQL compiler for EvaluateModel
@compiles(EvaluateModel)
def compile_evaluate_model(element, compiler, **kw):
    # Extract the arguments passed to the function
    model = compiler.process(literal_column(element.model), **kw)
    deployment_mode = compiler.process(literal_column(element.deployment_mode), **kw)
    replications = compiler.process(literal_column(element.replications), **kw)
    source_table = compiler.process(literal_column(element.source_table), **kw)

    # Create the SQL string
    evaluate_model_sql = ""
    if element.execution_mode == "EXECUTE":
        destination_table = compiler.process(literal_column(element.destination_table), **kw)
        evaluate_model_sql = f"""
EXECUTE FUNCTION EVALUATE_MODEL
(
    MODEL => {model},
    DEPLOYMENT_MODE => {deployment_mode},
    REPLICATIONS => {replications},
    SOURCE_TABLE => INPUT_TABLE
    (
        {source_table}
    ),
    DESTINATION_TABLE => '{destination_table}'
)"""
    else:
        evaluate_model_sql = f"""
SELECT * FROM TABLE
(
    EVALUATE_MODEL
    (
        MODEL => {model},
        DEPLOYMENT_MODE => {deployment_mode},
        REPLICATIONS => {replications},
        SOURCE_TABLE => INPUT_TABLE
        (
            {source_table}
        )
    )
)"""

    return evaluate_model_sql.strip()
