import os
import random
import sys

from sqlalchemy import (
    create_engine,
    Boolean,
    BIGINT,
    ARRAY,
    REAL,
    DOUBLE,
    VARCHAR,
    DECIMAL,
    UUID,
    DATE,
    TIME,
    TIMESTAMP,
    DATETIME,
    select,
    insert, text, MetaData, Table, Column, Integer, nullsfirst, asc, literal, func, and_, case, cast, desc, union,
    union_all, intersect, except_, column, alias, update, delete, )
# from sqlalchemy.sql import expression
from sqlalchemy.sql.ddl import CreateTable

from example_utils import *
from sqlalchemy_kinetica import kinetica_types
from sqlalchemy_kinetica.custom_commands import ki_insert as insert, CreateTableAs, Asof, \
    FirstValue, Pivot, PivotSelect, Unpivot, UnpivotSelect, ki_insert, FilterByString, EvaluateModel, KiUpdate
from sqlalchemy_kinetica.dialect import KineticaDialect
from sqlalchemy_kinetica.kinetica_types import (
    TINYINT,
    SMALLINT,
    VECTOR,
    UnsignedBigInteger,
    IPV4,
    BlobWKT,
    GEOMETRY,
    JSONArray,
    BLOB,
    FLOAT,
    DECIMAL,
)

ENV_URL = os.getenv("PY_TEST_URL", "http://localhost:9191")
ENV_USER = os.getenv("PY_TEST_USER", "")
ENV_PASS = os.getenv("PY_TEST_PASS", "")
ENV_SCHEMA = os.getenv("PY_TEST_SCHEMA", "sqlalchemy")
ENV_BYPASS_SSL_CERT_CHECK = os.getenv("PY_TEST_BYPASS_CERT_CHECK", True)
ENV_RECREATE_SCHEMA = os.getenv("PY_TEST_RECREATE_SCHEMA", False)

# Number of random records to generate
num_records = 10


def create_table_all_types(conn, schema):
    """
    Generates equivalent SQL to:

        CREATE OR REPLACE TABLE various_types
        (
            i   INTEGER NOT NULL,                                 /* non-nullable integer, part of primary key (defined at end)                         */
            ti  TINYINT,                                          /* native int8                                                                        */
            si  SMALLINT,                                         /* native int16                                                                       */
            bi  BIGINT,                                           /* native long                                                                        */
            ub  UNSIGNED BIGINT,                                  /* native unsigned long                                                               */
            b   BOOLEAN,                                          /* 0s and 1s only                                                                     */
            r   REAL,                                             /* native float                                                                       */
            d   DOUBLE,                                           /* native double                                                                      */
            dc  DECIMAL(10, 4),                                   /* native decimal                                                                     */
            s   VARCHAR(TEXT_SEARCH),                             /* string, searchable, only limited in size by system-configured value                */
            cd  VARCHAR(30, DICT),                                /* char32 using dictionary-encoding of values                                         */
            ct  VARCHAR(256, TEXT_SEARCH),                        /* char256, searchable                                                                */
            ip  IPV4,                                             /* IP address                                                                         */
            u   UUID(INIT_WITH_UUID),                             /* UUID                                                                               */
            td  DATE,                                             /* simple date                                                                        */
            tt  TIME,                                             /* simple time                                                                        */
            dt  DATETIME(INIT_WITH_NOW),                          /* date/time                                                                          */
            ts  TIMESTAMP,                                        /* timestamp                                                                          */
            j   JSON,                                             /* JSON string                                                                        */
            bl  BLOB,                                             /* native bytes                                                                       */
            w   BLOB(WKT),                                        /* geospatial column for WKT binary data                                              */
            g   GEOMETRY,                                         /* geospatial column for WKT string data                                              */
            ai  INTEGER[10],                                      /* array column holding 10 integer values                                             */
            v   VECTOR(10),                                       /* vector column holding 10 floating point values                                     */
            PRIMARY KEY (i)                                       /* primary key columns must be NOT NULL                                               */
        )

    See:  https://docs.kinetica.com/7.2/sql/ddl/#create-table

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    from sqlalchemy import MetaData, Table, Column, Integer, String

    metadata = MetaData()

    various_types = Table(
        "various_types",
        metadata,
        Column("i", Integer, primary_key = True),
        Column("ti", TINYINT),
        Column("si", SMALLINT),
        Column("bi", BIGINT),
        Column("ub", UnsignedBigInteger),
        Column("b", Boolean),
        Column("r", REAL),
        Column("d", DOUBLE),
        Column("dc", DECIMAL(10, 4)),
        Column("s", String, info = {"text_search": True}),
        Column("cd", VARCHAR(30), info = {"dict": True}),
        Column("ct", VARCHAR(256), info = {"text_search": True}),
        Column("ip", IPV4),
        Column("u", UUID, info = {"init_with_uuid": True}),
        Column("td", DATE),
        Column("tt", TIME),
        Column("dt", DATETIME, info = {"init_with_now": True}),
        Column("ts", TIMESTAMP),
        Column("j", kinetica_types.JSON),
        Column("bl", BLOB),
        Column("w", BlobWKT),
        Column("g", GEOMETRY),
        Column("ai", ARRAY(Integer, dimensions = 10)),
        Column("v", VECTOR(10)),
        schema = schema
    )
    metadata.create_all(conn.engine)

    print_statement("All-Types Table DDL", CreateTable(various_types).compile(conn))

    # Generate and insert random records
    for _ in range(num_records):
        record = generate_random_record()
        insert_stmt = insert(
            various_types, insert_hint = "KI_HINT_UPDATE_ON_EXISTING_PK"
        ).values(**record)
        conn.execute(insert_stmt)

    # Display the inserted rows using a select statement
    stmt = select(various_types)
    result = conn.execute(stmt)
    print_data("All-Types Table Data", stmt, result)


def create_table_replicated(conn, schema):
    """
    Generates equivalent SQL to:

        CREATE REPLICATED TABLE employee
        (
            id INTEGER NOT NULL,
            dept_id INTEGER NOT NULL,
            manager_id INTEGER,
            first_name VARCHAR(30),
            last_name VARCHAR(30),
            sal DECIMAL(18,4),
            hire_date DATE,
            work_district WKT,
            office_longitude REAL,
            office_latitude REAL,
            profile VECTOR(10),
            PRIMARY KEY (id)
        )

    See:  https://docs.kinetica.com/7.2/sql/ddl/#create-table

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    from sqlalchemy import MetaData, Table, Column, Integer, String

    metadata = MetaData()

    employee = Table(
        "employee",
        metadata,
        Column("id", Integer, nullable = False, primary_key = True),
        Column("dept_id", Integer, nullable = False, primary_key = True),
        Column("manager_id", Integer),
        Column("first_name", VARCHAR(30)),
        Column("last_name", VARCHAR(30)),
        Column("sal", DECIMAL(18, 4)),
        Column("hire_date", DATE),
        Column("work_district", BlobWKT),
        Column("office_longitude", REAL),
        Column("office_latitude", REAL),
        Column("profile", VECTOR(10)),
        schema = schema,
        prefixes = ["REPLICATED"]
    )

    print_statement("Employee Table DDL - Replicated", CreateTable(employee).compile(conn))
    
    metadata.create_all(conn.engine)


def create_table_sharded_with_options(conn, schema):
    """
    Generates equivalent SQL to:

        CREATE OR REPLACE TABLE employee
        (
            id INTEGER NOT NULL,
            dept_id INTEGER NOT NULL,
            manager_id INTEGER,
            first_name VARCHAR(30),
            last_name VARCHAR(30),
            sal DECIMAL(18,4),
            hire_date DATE,
            work_district WKT,
            office_longitude REAL,
            office_latitude REAL,
            profile VECTOR(10),
            PRIMARY KEY (id, dept_id),
            SHARD KEY (dept_id)
        )
        PARTITION BY RANGE (YEAR(hire_date))
        PARTITIONS
        (
            order_2018_2020 MIN(2018) MAX(2021),
            order_2021                MAX(2022),
            order_2022                MAX(2023),
            order_2023                MAX(2024)
        )
        TIER STRATEGY
        (
            ( ( VRAM 1, RAM 7, PERSIST 5 ) )
        )
        INDEX (dept_id)
        CHUNK SKIP INDEX (id)
        GEOSPATIAL INDEX (work_district)
        GEOSPATIAL INDEX (office_longitude, office_latitude)
        CAGRA INDEX (profile)
        USING TABLE PROPERTIES (CHUNK SIZE = 1000000, NO_ERROR_IF_EXISTS = true, TTL = 120)

    See:  https://docs.kinetica.com/7.2/sql/ddl/#create-table

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    from sqlalchemy import MetaData, Table, Column, Integer, String

    metadata = MetaData()

    table_properties = {
        "CHUNK SIZE": 1000000,
        "NO_ERROR_IF_EXISTS": "TRUE",
        "TTL": 120,
    }

    partition_clause = """
    PARTITION BY RANGE (YEAR(hire_date))
    PARTITIONS
    (
        order_2018_2020 MIN(2018) MAX(2021),
        order_2021                MAX(2022),
        order_2022                MAX(2023),
        order_2023                MAX(2024)
    )
    """

    employee = Table(
        "employee",
        metadata,
        Column("id", Integer, nullable = False, primary_key = True),
        Column("dept_id", Integer, nullable = False, primary_key = True, info = {"shard_key": True}),
        Column("manager_id", Integer),
        Column("first_name", VARCHAR(30)),
        Column("last_name", VARCHAR(30)),
        Column("sal", DECIMAL(18, 4)),
        Column("hire_date", DATE),
        Column("work_district", BlobWKT),
        Column("office_longitude", REAL),
        Column("office_latitude", REAL),
        Column("profile", VECTOR(10)),
        schema = schema,
        prefixes = ["OR REPLACE"],
        info = table_properties,
        kinetica_index = [["dept_id"]],
        kinetica_chunk_skip_index = "id",
        kinetica_geospatial_index = [["work_district"], ["office_longitude", "office_latitude"]],
        kinetica_cagra_index = ["profile"],
        kinetica_tier_strategy = "( ( VRAM 1, RAM 7, PERSIST 5 ) )",
        kinetica_partition_clause = partition_clause
    )
    
    print_statement("Employee Table DDL - Sharded with Options", CreateTable(employee).compile(conn))
    
    metadata.create_all(conn.engine)


def create_table_as(conn, schema):
    """
    Generates equivalent SQL to:

        CREATE OR REPLACE REPLICATED TEMP TABLE new_temporary_table AS
        (
            SELECT *
            FROM employee
        )

    See:  https://docs.kinetica.com/7.2/sql/ddl/#create-table-as

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """

    from sqlalchemy import MetaData, Table, Column, Integer, String

    metadata = MetaData()

    source_table = Table('employee', metadata, autoload_with = conn, schema = schema)

    # Quoting the table name for consistency here; only the user-defined schema may need it
    new_table_name = f"""{'"' + schema + '".' if schema else ''}"new_temporary_table" """

    create_stmt = CreateTableAs(
            new_table_name,
            select(source_table),
            prefixes = ["OR REPLACE", "REPLICATED", "TEMP"]
    )

    create_stmt = create_stmt.compile(conn)

    print_statement("CREATE TABLE...AS", create_stmt)
    
    conn.execute(create_stmt)


def create_datasource(conn, schema, url, username, password):
    SQL_CREATE_DATA_SOURCE = """
CREATE OR REPLACE DATA SOURCE {}
LOCATION = '{}'
USER = '{}'
PASSWORD = '{}'
    """

    create_stmt = SQL_CREATE_DATA_SOURCE.format(
        f"""{'"' + schema + '".' if schema else ''}jdbc_ds""",
        f"jdbc:kinetica:URL={url}",
        username,
        password
    )

    print_statement("CREATE DATA SOURCE", create_stmt)

    conn.execute(text(create_stmt))


def create_external_table(conn, schema):
    """
    Generates equivalent SQL to:

        CREATE EXTERNAL TABLE remote_employee
        REMOTE QUERY 'SELECT * EXCLUDE(profile) FROM employee'
        WITH OPTIONS
        (
            DATA SOURCE = 'jdbc_ds',
            SUBSCRIBE = TRUE,
            REMOTE_QUERY_INCREASING_COLUMN = 'id'
        )
        USING TABLE PROPERTIES (CHUNK SIZE = 1000000, NO_ERROR_IF_EXISTS = true, TTL = 120)

    See:  https://docs.kinetica.com/7.2/sql/ddl/#create-external-table

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """

    from sqlalchemy import MetaData, Table

    metadata = MetaData()

    remote_table_name = f"""{'"' + schema + '".' if schema else ''}employee"""
    data_source_name = f"""{schema + '.' if schema else ''}jdbc_ds"""

    external_table = Table(
        "remote_employee",
        metadata,
        schema = schema,
        prefixes = ["EXTERNAL"],
        info = {
            "CHUNK SIZE": 1000000,
            "NO_ERROR_IF_EXISTS": "TRUE",
            "TTL": 120
        },
        kinetica_external_table_remote_query = f"SELECT * EXCLUDE(profile) FROM {remote_table_name}",
        kinetica_external_table_option = {
            'DATA SOURCE': data_source_name,
            'SUBSCRIBE': 'TRUE',
            'REMOTE_QUERY_INCREASING_COLUMN': 'id'
        }
    )

    create_stmt = CreateTable(external_table).compile(dialect = KineticaDialect())

    print_statement("CREATE EXTERNAL TABLE", create_stmt)

    conn.execute(create_stmt)


def create_example_tables(conn, schema):
    """
    Creates tables used by examples:

    * insert_from_select()
    * insert_with_cte()
    * select_join_asof()
    * select_join_asof_filter()
    * select_pivot()
    * select_unpivot()
    * select_union()
    * select_union_all()
    * select_intersect()
    * select_except()
    * table_function_filter_by_string()

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """

    metadata = MetaData()


    # Create the target table for the INSERT from SELECT example
    employee_backup = Table(
        "employee_backup",
        metadata,
        Column("id", Integer, nullable = False, primary_key = True),
        Column("dept_id", Integer, nullable = False, primary_key = True, info = {"shard_key": True}),
        Column("manager_id", Integer),
        Column("first_name", VARCHAR(30)),
        Column("last_name", VARCHAR(30)),
        Column("sal", DECIMAL(18, 4)),
        schema = schema
    )
    employee_backup.create(conn)


    # Create the target table for the INSERT with CTE example
    dept2_roster = Table(
        "dept2_emp_mgr_roster",
        metadata,
        Column("emp_first_name", VARCHAR(30)),
        Column("emp_last_name", VARCHAR(30)),
        Column("mgr_first_name", VARCHAR(30)),
        Column("mgr_last_name", VARCHAR(30)),
        schema = schema
    )
    dept2_roster.create(conn)


    # Create the source tables for the ASOF join examples
    quotes = Table(
        "quotes",
        metadata,
        Column("symbol", VARCHAR(4)),
        Column("open_dt", DATETIME),
        Column("open_price", DECIMAL(7,4)),
        schema = schema,
        prefixes = ["REPLICATED"]
    )
    quotes.create(conn)

    trades = Table(
        "trades",
        metadata,
        Column("id", Integer),
        Column("ticker", VARCHAR(4)),
        Column("dt", DATETIME),
        Column("price", DECIMAL(7,4)),
        schema = schema
    )
    trades.create(conn)

    # Insert example data
    cnames = ["symbol", "open_dt", "open_price"]
    data = [
        ['EBAY', '2006-12-14 05:00:00', 31.24],
        ['EBAY', '2006-12-15 05:00:00', 32.97],
        ['EBAY', '2006-12-16 05:00:00', 39.93]
    ]
    records = [ {key: val for key, val in zip(cnames, record)} for record in data ]

    conn.execute(ki_insert(quotes), records)

    cnames = ["id", "ticker", "dt", "price"]
    data = [
        [1, 'EBAY', '2006-12-15 10:20:30', 30.06],
        [2, 'EBAY', '2016-12-15 11:22:33', 33.16],
        [3, 'ABCD', '2006-12-15 12:24:36', 1224.06],
        [4, 'ABCD', '2016-12-15 13:26:42', 1326.16]
    ]
    records = [ {key: val for key, val in zip(cnames, record)} for record in data ]

    conn.execute(ki_insert(trades), records)


    # Create the source table for the PIVOT example
    phone_list = Table(
        "phone_list",
        metadata,
        Column("name", VARCHAR(4)),
        Column("phone_type", VARCHAR(4)),
        Column("phone_number", VARCHAR(16)),
        schema = schema
    )
    phone_list.create(conn)

    # Insert example data
    cnames = ["name", "phone_type", "phone_number"]
    data = [
        ['Jane', 'Home', '123-456-7890'],
        ['Jane', 'Work', '111-222-3333'],
        ['John', 'Home', '123-456-7890'],
        ['John', 'Cell', '333-222-1111']
    ]
    records = [ {key: val for key, val in zip(cnames, record)} for record in data ]

    conn.execute(ki_insert(phone_list), records)


    # Create the source table for the UNPIVOT example
    customer_contact = Table(
        "customer_contact",
        metadata,
        Column("name", VARCHAR(4)),
        Column("home_phone", VARCHAR(16)),
        Column("work_phone", VARCHAR(16)),
        Column("cell_phone", VARCHAR(16)),
        schema = schema
    )
    customer_contact.create(conn)

    # Insert example data
    cnames = ["name", "home_phone", "work_phone", "cell_phone"]
    data = [
        ['Jane', '123-456-7890', '111-222-3333', None],
        ['John', '123-456-7890', None, '333-222-1111']
    ]
    records = [ {key: val for key, val in zip(cnames, record)} for record in data ]

    conn.execute(ki_insert(customer_contact), records)


    # Create the source tables for the UNION, UNION ALL, INTERSECT, & EXCEPT examples
    cnames = ["id", "food_name", "category", "price"]

    lunch_menu = Table(
        "lunch_menu",
        metadata,
        Column(cnames[0], Integer, primary_key = True),
        Column(cnames[1], VARCHAR(32)),
        Column(cnames[2], VARCHAR(8)),
        Column(cnames[3], DECIMAL(5,2)),
        schema = schema
    )
    lunch_menu.create(conn)

    dinner_menu = Table(
        "dinner_menu",
        metadata,
        Column(cnames[0], Integer, primary_key = True),
        Column(cnames[1], VARCHAR(32)),
        Column(cnames[2], VARCHAR(8)),
        Column(cnames[3], DECIMAL(5,2)),
        schema = schema
    )
    dinner_menu.create(conn)

    # Insert example data
    data = [
        [1, "Porridge", "soup", "10.99"],
        [2, "Cream of marshroom soup", "soup", "11.99"],
        [3, "Cactus steak", "steak", "19.99"],
        [4, "Bunicorn steak", "steak", "18.99"],
        [5, "Squid-on-a-stick", "seafood", "13.99"],
        [6, "Sardine-on-a-stick", "seafood", "9.99"],
        [7, "Potato Salad", "salad", "12.99"],
        [8, "Fruit Salad", "salad", "14.99"]
    ]
    records = [ {key: val for key, val in zip(cnames, record)} for record in data ]

    conn.execute(ki_insert(lunch_menu), records)

    data = [
        [1, "Sailor's stew", "soup", "13.99"],
        [2, "Bouillabaisse", "soup", "16.99"],
        [3, "Cactus steak", "steak", "19.99"],
        [4, "Bony steak", "steak", "26.99"],
        [5, "Squid-on-a-stick", "seafood", "15.99"],
        [6, "Fresh Fish Feast", "seafood", "31.99"],
        [7, "Potato Salad", "salad", "14.99"],
        [8, "Super Salad", "salad", "24.99"]
    ]
    records = [ {key: val for key, val in zip(cnames, record)} for record in data ]

    conn.execute(ki_insert(dinner_menu), records)


    # Create the source table for the FILTER_BY_STRING example
    cnames = ["event_time", "message"]

    event_log = Table(
        "event_log",
        metadata,
        Column(cnames[0], DATETIME),
        Column(cnames[1], VARCHAR(256)),
        schema = schema
    )
    event_log.create(conn)

    # Insert example data
    data = [
        ['2020-01-02 03:04:05', '[INFO] This is some information'],
        ['2021-02-03 04:05:06', '[WARN] This is a warning'],
        ['2022-03-04 05:06:07', '[ERROR] This is an error']
    ]
    records = [ {key: val for key, val in zip(cnames, record)} for record in data ]

    conn.execute(ki_insert(event_log), records)


def insert_multiple_records(conn, schema):
    """
    Generates equivalent SQL to:

        INSERT INTO employee (id, dept_id, manager_id, first_name, last_name, sal, hire_date)
        VALUES
            (1, 1, null, 'Anne',     'Arbor',   200000,      '2000-01-01'),
            (2, 2,    1, 'Brooklyn', 'Bridges', 100000,      '2000-02-01'),
            (3, 3,    1, 'Cal',      'Cutta',   100000,      '2000-03-01'),
            (4, 2,    2, 'Dover',    'Della',   150000,      '2000-04-01'),
            (5, 2,    2, 'Elba',     'Eisle',    50000,      '2000-05-01'),
            (6, 4,    1, 'Frank',    'Furt',     12345.6789, '2000-06-01')

    See:  https://docs.kinetica.com/7.2/sql/dml/#insert-into-values

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    #   The UPDATE_ON_EXISTING_PK hint can be used to invoke upsert mode,
    #   which will overwrite any existing record with the same PK with the new record
    employee = Table('employee', metadata, autoload_with = conn, schema = schema)

    # Define the insert statement with values
    records = [
        {"id": 1, "dept_id": 1, "manager_id": None, "first_name": "Anne",     "last_name": "Arbor",   "sal": 200000,      "hire_date": "2000-01-01"},
        {"id": 2, "dept_id": 2, "manager_id":    1, "first_name": "Brooklyn", "last_name": "Bridges", "sal": 100000,      "hire_date": "2000-02-01"},
        {"id": 3, "dept_id": 3, "manager_id":    1, "first_name": "Cal",      "last_name": "Cutta",   "sal": 100000,      "hire_date": "2000-03-01"},
        {"id": 4, "dept_id": 2, "manager_id":    2, "first_name": "Dover",    "last_name": "Della",   "sal": 150000,      "hire_date": "2000-04-01"},
        {"id": 5, "dept_id": 2, "manager_id":    2, "first_name": "Elba",     "last_name": "Eisle",   "sal":  50000,      "hire_date": "2000-05-01"},
        {"id": 6, "dept_id": 4, "manager_id":    1, "first_name": "Frank",    "last_name": "Furt",    "sal":  12345.6789, "hire_date": "2000-06-01"}
    ]

    insert_stmt = ki_insert(employee, insert_hint = "KI_HINT_UPDATE_ON_EXISTING_PK")

    print_statement("Insert Multiple Records Statement", insert_stmt.compile(conn))

    check_data("Insert Multiple Records Data (Before)", metadata, conn, schema, 'employee', 'id')

    conn.execute(insert_stmt, records)

    check_data("Insert Multiple Records Data (After)", metadata, conn, schema, 'employee', 'id')


def insert_from_select(conn, schema):
    """
    Generates equivalent SQL to:

        INSERT INTO employee_backup (id, dept_id, manager_id, first_name, last_name, sal)
        SELECT id, dept_id, manager_id, first_name, last_name, sal
        FROM employee
        WHERE hire_date >= '2000-04-01'

    See:  https://docs.kinetica.com/7.2/sql/dml/#insert-into-select

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create handles to the source & target tables
    employee = Table('employee', metadata, autoload_with = conn, schema = schema)
    employee_backup = Table('employee_backup', metadata, autoload_with = conn, schema = schema)

    # Prepare the insert statement with a select clause
    insert_stmt = insert(employee_backup).from_select(
        ["id", "dept_id", "manager_id", "first_name", "last_name", "sal"],                  # The columns to insert into
        select(employee.c["id", "dept_id", "manager_id", "first_name", "last_name", "sal"])   # The select statement providing the data
    )

    print_statement("Insert From Select Statement", insert_stmt.compile(conn))

    check_data("Insert From Select Data (Before)", metadata, conn, schema, 'employee_backup', 'id')

    conn.execute(insert_stmt)

    check_data("Insert From Select Data (After)", metadata, conn, schema, 'employee_backup', 'id')


def insert_with_cte(conn, schema):
    """
    Generates equivalent SQL to (WITH in INSERT Example):

        INSERT INTO dept2_emp_mgr_roster (emp_first_name, emp_last_name, mgr_first_name, mgr_last_name)
        WITH
            dept2_emp AS
            (
                SELECT first_name, last_name, manager_id
                FROM employee
                WHERE dept_id = 2
            ),
            dept2_mgr AS
            (
                SELECT first_name, last_name, id
                FROM employee
                WHERE dept_id = 2
            )
        SELECT d2emp.first_name, d2emp.last_name, d2mgr.first_name, d2mgr.last_name
        FROM
            dept2_emp as d2emp
            JOIN dept2_mgr as d2mgr ON d2emp.manager_id = d2mgr.id

    See:  https://docs.kinetica.com/7.2/sql/query/#with-common-table-expressions

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """

    metadata = MetaData()

    # Create handles to the source & target tables
    employee = Table('employee', metadata, autoload_with = conn, schema = schema)
    dept2_roster = Table('dept2_emp_mgr_roster', metadata, autoload_with = conn, schema = schema)

    # Define the first CTE for dept2_emp
    dept2_emp = (
        select(employee.c.first_name, employee.c.last_name, employee.c.manager_id)
        .where(employee.c.dept_id == 2)
        .cte(name = 'dept2_emp')
    )

    # Define the second CTE for dept2_mgr
    dept2_mgr = (
        select(employee.c.first_name, employee.c.last_name, employee.c.id)
        .where(employee.c.dept_id == 2)
        .cte(name = 'dept2_mgr')
    )

    # Define the SELECT statement that joins the CTEs
    select_stmt = (
        select(
            dept2_emp.c.first_name.label('emp_first_name'),
            dept2_emp.c.last_name.label('emp_last_name'),
            dept2_mgr.c.first_name.label('mgr_first_name'),
            dept2_mgr.c.last_name.label('mgr_last_name')
        )
        .select_from(
            dept2_emp.join(dept2_mgr, dept2_emp.c.manager_id == dept2_mgr.c.id)
        )
    )

    # Define the INSERT statement using a list of columns to insert into and the SELECT statement
    insert_stmt = dept2_roster.insert().from_select(
        [
            'emp_first_name',
            'emp_last_name',
            'mgr_first_name',
            'mgr_last_name'
        ],
        select_stmt
    )

    # Compile the query
    compiled_query = insert_stmt.compile(conn, compile_kwargs = {"literal_binds": True})

    # Print the compiled SQL query
    print_statement("Insert with Common Table Expression (WITH)", compiled_query)

    check_data("Insert From CTE Data (Before)", metadata, conn, schema, 'dept2_emp_mgr_roster', 'emp_first_name')

    # conn.execute(text(str(compiled_query)))
    conn.execute(compiled_query)

    check_data("Insert From CTE Data (After)", metadata, conn, schema, 'dept2_emp_mgr_roster', 'emp_first_name')


def select_with_cte(conn, schema):
    """
    Generates equivalent SQL to (WITH Example):

        WITH
            dept2_emp_sal_by_mgr (manager_id, salary) AS
            (
                SELECT manager_id, sal
                FROM employee
                WHERE dept_id = 2
            )
        SELECT
            manager_id dept2_mgr_id,
            MAX(salary) dept2_highest_emp_sal_per_mgr,
            COUNT(*) as dept2_total_emp_per_mgr
        FROM dept2_emp_sal_by_mgr
        GROUP BY manager_id

    See:  https://docs.kinetica.com/7.2/sql/query/#with-common-table-expressions

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """

    metadata = MetaData()

    # Create a handle to the source table
    employee = Table('employee', metadata, autoload_with = conn, schema = schema)

    # Define the CTE (Common Table Expression)
    dept2_emp_sal_by_mgr = (
        select(employee.c.manager_id, employee.c.sal.label('salary'))
        .where(employee.c.dept_id == 2)
        .cte(name = 'dept2_emp_sal_by_mgr')
    )

    # Define the main query using the CTE
    query = (
        select(
            dept2_emp_sal_by_mgr.c.manager_id.label('dept2_mgr_id'),
            func.max(dept2_emp_sal_by_mgr.c.salary).label('dept2_highest_emp_sal_per_mgr'),
            func.count().label('dept2_total_emp_per_mgr')
        )
        .group_by(dept2_emp_sal_by_mgr.c.manager_id)
    )

    # Compile the query
    compiled_query = query.compile(conn)

    result = conn.execute(compiled_query)
    print_data("Common Table Expressions (WITH)", compiled_query, result)


def select_join_infixed(conn, schema):
    """
    Generates equivalent SQL to:

        SELECT
            e.last_name || ', ' || e.first_name AS "Employee_Name",
            m.last_name || ', ' || m.first_name AS "Manager_Name"
        FROM
            employee e
            LEFT JOIN employee m ON e.manager_id = m.id
        WHERE
            e.dept_id IN (1, 2, 3)
        ORDER BY
            m.id ASC NULLS FIRST,
            e.hire_date

    See:  https://docs.kinetica.com/7.2/sql/query/#join

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    employee = Table('employee', metadata, autoload_with = conn, schema = schema)

    # Aliases for self-join
    e = employee.alias("e")
    m = employee.alias("m")

    # Construct the query
    query = select(
        (e.c.last_name + ', ' + e.c.first_name).label("Employee_Name"),
        (m.c.last_name + ', ' + m.c.first_name).label("Manager_Name")
    ).select_from(
        e.outerjoin(m, e.c.manager_id == m.c.id)
    ).where(
        e.c.dept_id.in_([1, 2, 3])
    ).order_by(
        nullsfirst(asc(m.c.id)),
        e.c.hire_date
    )

    result = conn.execute(query)

    print_data("Infixed JOIN", query.compile(conn, compile_kwargs = {"literal_binds": True}), result)


def select_join_non_infixed(conn, schema):
    """
    Generates equivalent SQL to:

        SELECT
            e.last_name || ', ' || e.first_name AS "Employee_Name",
            m.last_name || ', ' || m.first_name AS "Manager_Name"
        FROM
            employee e,
            employee m
        WHERE
            e.manager_id = m.id
        ORDER BY
            e.last_name,
            e.first_name

    See:  https://docs.kinetica.com/7.2/sql/query/#join

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    employee_table = Table('employee', metadata, autoload_with = conn, schema = schema)

    # Aliasing the table for the manager
    manager_alias = employee_table.alias('m')

    # Constructing the query
    query = select(
        (employee_table.c.last_name + ', ' + employee_table.c.first_name).label("Employee_Name"),
        (manager_alias.c.last_name + ', ' + manager_alias.c.first_name).label("Manager_Name")
    ).where(
        employee_table.c.manager_id == manager_alias.c.id
    ).order_by(
        employee_table.c.last_name.asc(),
        employee_table.c.first_name.asc()
    )

    result = conn.execute(query)

    print_data("Non-Infixed JOIN", query.compile(conn, compile_kwargs = {"literal_binds": True}), result)


def select_join_asof(conn, schema):
    """
    Generates equivalent SQL to (ASOF JOIN):

        SELECT
            t.id,
            t.dt AS execution_dt,
            q.open_dt AS quote_dt,
            t.price AS execution_price,
            q.open_price
        FROM
            trades t
            LEFT JOIN quotes q ON
                t.ticker = q.symbol AND
                ASOF(t.dt, q.open_dt, INTERVAL '-1' DAY, INTERVAL '0' DAY, MAX)

    See:  https://docs.kinetica.com/7.2/sql/query/#asof

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create handles to the source tables
    q = Table('quotes', metadata, autoload_with = conn, schema = schema).alias("q")
    t = Table('trades', metadata, autoload_with = conn, schema = schema).alias("t")

    # Define the ASOF function in the query
    asof_condition = Asof(
        t.c.dt,
        q.c.open_dt,
        text("INTERVAL '-1' DAY"),
        text("INTERVAL '0' DAY"),
        text("MAX")
    )

    # Construct the SELECT statement
    query = select(
        t.c.id,
        t.c.dt.label('execution_dt'),
        q.c.open_dt.label('quote_dt'),
        t.c.price.label('execution_price'),
        q.c.open_price
    ).select_from(
        t.outerjoin(
            q, (t.c.ticker == q.c.symbol) & asof_condition
        )
    )

    # Compile the query to see the generated SQL
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(query)
    print_data("ASOF JOIN", compiled_query, result)


def select_join_asof_filter(conn, schema):
    """
    Generates equivalent SQL to (ASOF JOIN with FILTER):

        SELECT
            t.ticker,
            t.asof_dt,
            q.open_dt,
            q.open_price
        FROM
            (SELECT 'EBAY' AS ticker, DATETIME('2006-12-15 12:34:56') AS asof_dt) t
            LEFT JOIN quotes q ON
                t.ticker = q.symbol AND
                ASOF(t.asof_dt, q.open_dt, INTERVAL '-1' DAY, INTERVAL '0' DAY, MAX);

    See:  https://docs.kinetica.com/7.2/sql/query/#asof

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    q = Table('quotes', metadata, autoload_with = conn, schema = schema).alias("q")

    # Define the subquery 't'
    t = (
        select(
        literal('EBAY').label('ticker'),
        func.datetime('2006-12-15 12:34:56').label('asof_dt')
        ).subquery('t')
    )

    # Construct the full query
    query = select(
        t.c.ticker,
        t.c.asof_dt,
        q.c.open_dt,
        q.c.open_price
    ).select_from(
        t.outerjoin(
            q,
            and_(
                t.c.ticker == q.c.symbol,
                Asof(
                    t.c.asof_dt,
                    q.c.open_dt,
                    text("INTERVAL '-1' DAY"),
                    text("INTERVAL '0' DAY"),
                    text("MAX")
                )
            )
        )
    )

    # Compile the query to see the generated SQL
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(query)
    print_data("ASOF JOIN as Filter", compiled_query, result)
    

def select_aggregation_without_groupby(conn):
    """
    Generates equivalent SQL to (Aggregation without GROUP BY Example):

        SELECT ROUND(AVG(total_amount),2) AS "Average_Fare"
        FROM demo.nyctaxi

    See:  https://docs.kinetica.com/7.2/sql/query/#aggregation

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    nyctaxi = Table('nyctaxi', metadata, autoload_with = conn, schema = 'demo')

    # Define the select statement
    query = select(
        func.round(func.avg(nyctaxi.c.total_amount), 2).label('Average_Fare')
    )

    # Compile the query
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(compiled_query)
    print_data("Aggregate without GROUP BY", compiled_query, result)


def select_aggregation_with_groupby(conn):
    """
    Generates equivalent SQL to (Aggregate with GROUP BY Example):

        SELECT
            vendor_id AS Vendor_ID,
            YEAR(pickup_datetime) AS Year,
            MAX(trip_distance) AS Max_Trip,
            MIN(trip_distance) AS Min_Trip,
            ROUND(AVG(trip_distance),2) AS Avg_Trip,
            INT(AVG(passenger_count)) AS Avg_Passenger_Count
        FROM demo.nyctaxi
        WHERE
            trip_distance > 0 AND
            trip_distance < 100
        GROUP BY vendor_id, 2
        ORDER BY Vendor_ID, Year

    See:  https://docs.kinetica.com/7.2/sql/query/#aggregation

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    nyctaxi = Table('nyctaxi', metadata, autoload_with = conn, schema = 'demo')

    # Define the select statement
    query = select(
        nyctaxi.c.vendor_id.label('Vendor_ID'),
        func.year(nyctaxi.c.pickup_datetime).label('Year'),
        func.max(nyctaxi.c.trip_distance).label('Max_Trip'),
        func.min(nyctaxi.c.trip_distance).label('Min_Trip'),
        func.round(func.avg(nyctaxi.c.trip_distance), 2).label('Avg_Trip'),
        func.cast(func.avg(nyctaxi.c.passenger_count), Integer).label('Avg_Passenger_Count')
    ).where(
        and_(
            nyctaxi.c.trip_distance > 0,
            nyctaxi.c.trip_distance < 100
        )
    ).group_by(
        nyctaxi.c.vendor_id,
        func.year(nyctaxi.c.pickup_datetime)
    ).order_by(
        nyctaxi.c.vendor_id.asc(),
        func.year(nyctaxi.c.pickup_datetime).asc()
    )

    # Compile the query
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(compiled_query)
    print_data("Aggregate with GROUP BY", compiled_query, result)


def select_aggregation_rollup(conn):
    """
    Generates equivalent SQL to (ROLLUP Example):

        SELECT
            CASE
                WHEN (GROUPING(Sector) = 1) THEN '<ALL SECTORS>'
                ELSE NVL(Sector, '<UNKNOWN SECTOR>')
            END AS Sector_Group,
            CASE
                WHEN (GROUPING(Symbol) = 1) THEN '<ALL SYMBOLS>'
                ELSE NVL(Symbol, '<UNKNOWN SYMBOL>')
            END AS Symbol_Group,
            AVG("Open") AS AvgOpen
        FROM demo.stocks
        GROUP BY ROLLUP(Sector, Symbol)
        ORDER BY Sector_Group, Symbol_Group

    See:  https://docs.kinetica.com/7.2/sql/query/#sql-grouping-rollup

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    stocks = Table('stocks', metadata, autoload_with = conn, schema = 'demo')

    # Define the select statement
    sector_group = case(
        (func.grouping(stocks.c.Sector) == 1, '<ALL SECTORS>'),
        else_ = func.nvl(stocks.c.Sector, '<UNKNOWN SECTOR>')
    ).label('Sector_Group')

    symbol_group = case(
        (func.grouping(stocks.c.Symbol) == 1, '<ALL SYMBOLS>'),
        else_ = func.nvl(stocks.c.Symbol, '<UNKNOWN SYMBOL>')
    ).label('Symbol_Group')

    query = select(
        sector_group,
        symbol_group,
        func.avg(stocks.c.Open).label('AvgOpen')
    ).group_by(
        func.rollup(stocks.c.Sector, stocks.c.Symbol)
    ).order_by(
        sector_group.asc(),
        symbol_group.asc()
    )
    # Compile the query
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(compiled_query)
    print_data("Aggregate with ROLLUP", compiled_query, result)


def select_aggregation_cube(conn):
    """
    Generates equivalent SQL to (CUBE Example):

        SELECT
            CASE
                WHEN (GROUPING(Sector) = 1) THEN '<ALL SECTORS>'
                ELSE NVL(Sector, '<UNKNOWN SECTOR>')
            END AS Sector_Group,
            CASE
                WHEN (GROUPING(Symbol) = 1) THEN '<ALL SYMBOLS>'
                ELSE NVL(Symbol, '<UNKNOWN SYMBOL>')
            END AS Symbol_Group,
            AVG("Open") AS AvgOpen
        FROM demo.stocks
        GROUP BY CUBE(Sector, Symbol)
        ORDER BY Sector_Group, Symbol_Group

    See:  https://docs.kinetica.com/7.2/sql/query/#sql-grouping-cube

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    stocks = Table('stocks', metadata, autoload_with = conn, schema = 'demo')

    # Define the CASE statements
    sector_group = case(
        (func.grouping(stocks.c.Sector) == 1, '<ALL SECTORS>'),
        else_ = func.nvl(stocks.c.Sector, '<UNKNOWN SECTOR>')
    ).label('Sector_Group')

    symbol_group = case(
        (func.grouping(stocks.c.Symbol) == 1, '<ALL SYMBOLS>'),
        else_ = func.nvl(stocks.c.Symbol, '<UNKNOWN SYMBOL>')
    ).label('Symbol_Group')

    # Define the query
    query = select(
        sector_group,
        symbol_group,
        func.avg(stocks.c.Open).label('AvgOpen')
    ).group_by(
        func.cube(stocks.c.Sector, stocks.c.Symbol)
    ).order_by(
        sector_group.asc(),
        symbol_group.asc()
    )

    # Compile the query
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(compiled_query)
    print_data("Aggregate with CUBE", compiled_query, result)


def select_aggregation_grouping_sets(conn):
    """
    Generates equivalent SQL to (GROUPING SETS Example):

        SELECT
            CASE
                WHEN (GROUPING(Sector) = 1) THEN '<ALL SECTORS>'
                ELSE NVL(Sector, '<UNKNOWN SECTOR>')
            END AS Sector_Group,
            CASE
                WHEN (GROUPING(Symbol) = 1) THEN '<ALL SYMBOLS>'
                ELSE NVL(Symbol, '<UNKNOWN SYMBOL>')
            END AS Symbol_Group,
            AVG("Open") AS AvgOpen
        FROM demo.stocks
        GROUP BY GROUPING SETS((Sector), (Symbol), ())
        ORDER BY Sector_Group, Symbol_Group

    See:  https://docs.kinetica.com/7.2/sql/query/#sql-grouping-groupingsets

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    stocks = Table('stocks', metadata, autoload_with = conn, schema = 'demo')

    # Define the CASE statements
    sector_group = case(
        (func.grouping(stocks.c.Sector) == 1, '<ALL SECTORS>'),
        else_ = func.nvl(stocks.c.Sector, '<UNKNOWN SECTOR>')
    ).label('Sector_Group')

    symbol_group = case(
        (func.grouping(stocks.c.Symbol) == 1, '<ALL SYMBOLS>'),
        else_ = func.nvl(stocks.c.Symbol, '<UNKNOWN SYMBOL>')
    ).label('Symbol_Group')

    # Use raw SQL for GROUPING SETS
    # There is no direct construct in SQLAlchemy to support this
    # so, it's best to model it as raw text SQL
    grouping_sets_clause = text('GROUPING SETS((Sector), (Symbol), ())')

    # Define the query
    query = select(
        sector_group,
        symbol_group,
        func.avg(stocks.c.Open).label('AvgOpen')
    ).group_by(grouping_sets_clause).order_by(
        sector_group.asc(),
        symbol_group.asc()
    )

    # Compile the query
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(compiled_query)
    print_data("Aggregate with GROUPING SETS", compiled_query, result)


def select_window_rolling_sum(conn):
    """
    Generates equivalent SQL to (Window Rolling Sum Example):

        SELECT
            vendor_id,
            pickup_datetime,
            total_amount,
            passenger_count,
            DECIMAL
            (
                SUM(total_amount) OVER
                    (
                        PARTITION BY vendor_id
                        ORDER BY pickup_datetime
                    )
            ) AS growing_sum,
            COUNT(*) OVER
                (
                    PARTITION BY vendor_id
                    ORDER BY LONG(pickup_datetime)
                    RANGE BETWEEN 300000 PRECEDING AND 300000 FOLLOWING
                ) AS trip_demand
        FROM demo.nyctaxi
        WHERE pickup_datetime >= '2015-01-01' AND pickup_datetime < '2015-01-01 02:00:00'
        ORDER BY
            vendor_id,
            pickup_datetime

    See:  https://docs.kinetica.com/7.2/sql/query/#window

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    nyctaxi = Table('nyctaxi', metadata, autoload_with = conn, schema = 'demo').alias("n")

    # Define the SUM window function
    growing_sum = func.sum(nyctaxi.c.total_amount).over(
        partition_by = nyctaxi.c.vendor_id,
        order_by = nyctaxi.c.pickup_datetime
    ).label('growing_sum')

    # Define the COUNT window function with RANGE and casting
    trip_demand = func.count(text('*')).over(
        partition_by = nyctaxi.c.vendor_id,
        order_by = nyctaxi.c.pickup_datetime,
        range_ = (-300000, 300000)
    ).label('trip_demand')

    # Define the query
    query = select(
        nyctaxi.c.vendor_id,
        func.datetime(nyctaxi.c.pickup_datetime).label("pickup_datetime"),
        nyctaxi.c.total_amount,
        nyctaxi.c.passenger_count,
        growing_sum,
        trip_demand
    ).where(
        nyctaxi.c.pickup_datetime >= '2015-01-01',
        nyctaxi.c.pickup_datetime < '2015-01-01 02:00:00'
    ).order_by(
        nyctaxi.c.vendor_id,
        nyctaxi.c.pickup_datetime
    )

    # Compile the query
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(compiled_query)
    print_data("Window Function - Rolling Sum", compiled_query, result)


def select_window_moving_average(conn):
    """
    Generates equivalent SQL to (Window Moving Average Example):

        SELECT
            vendor_id,
            pickup_datetime,
            trip_distance,
            AVG(trip_distance) OVER
                (
                    PARTITION BY vendor_id
                    ORDER BY pickup_datetime
                    ROWS BETWEEN 5 PRECEDING AND 10 FOLLOWING
                ) AS local_avg_dist
        FROM demo.nyctaxi
        WHERE
            passenger_count = 4 AND
            pickup_datetime >= '2015-01-01' AND pickup_datetime < '2015-01-02'
        ORDER BY
            vendor_id,
            pickup_datetime

    See:  https://docs.kinetica.com/7.2/sql/query/#window

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    nyctaxi = Table('nyctaxi', metadata, autoload_with = conn, schema = 'demo')

    # Define the AVG window function with ROWS BETWEEN 5 PRECEDING AND 10 FOLLOWING
    local_avg_dist = func.avg(nyctaxi.c.trip_distance).over(
        partition_by = nyctaxi.c.vendor_id,
        order_by = nyctaxi.c.pickup_datetime,
        rows = (-5, 10)  # This sets ROWS BETWEEN 5 PRECEDING AND 10 FOLLOWING
    ).label('local_avg_dist')

    # Define the query
    query = select(
        nyctaxi.c.vendor_id,
        func.datetime(nyctaxi.c.pickup_datetime).label("pickup_datetime"),
        nyctaxi.c.trip_distance,
        local_avg_dist
    ).where(
        nyctaxi.c.passenger_count == 4,
        nyctaxi.c.pickup_datetime >= '2015-01-01',
        nyctaxi.c.pickup_datetime < '2015-01-02'
    ).order_by(
        nyctaxi.c.vendor_id,
        nyctaxi.c.pickup_datetime
    )

    # Compile the query
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(compiled_query)
    print_data("Window Function - Moving Average", compiled_query, result)


def select_window_ranking(conn):
    """
    Generates equivalent SQL to (Window Ranking Example):

        SELECT
            vendor_id,
            pickup_datetime,
            dropoff_datetime,
            total_amount AS fare,
            RANK() OVER (PARTITION BY vendor_id ORDER BY total_amount) AS ranked_fare,
            DECIMAL(PERCENT_RANK() OVER (PARTITION BY vendor_id ORDER BY total_amount)) * 100 AS percent_ranked_fare
        FROM demo.nyctaxi
        WHERE
            passenger_count = 3 AND
            pickup_datetime >= '2015-01-11' AND pickup_datetime < '2015-01-12'
        ORDER BY
            vendor_id,
            pickup_datetime

    See:  https://docs.kinetica.com/7.2/sql/query/#window

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    nyctaxi = Table('nyctaxi', metadata, autoload_with = conn, schema = 'demo')

    # Define the RANK() window function
    ranked_fare = func.rank().over(
        partition_by = nyctaxi.c.vendor_id,
        order_by = nyctaxi.c.total_amount
    ).label('ranked_fare')

    percent_ranked_fare = func.percent_rank().over(
                partition_by = nyctaxi.c.vendor_id,
                order_by = nyctaxi.c.total_amount
            ) * 100

    # Define the query
    query = select(
        nyctaxi.c.vendor_id,
        func.datetime(nyctaxi.c.pickup_datetime).label("pickup_datetime"),
        func.datetime(nyctaxi.c.dropoff_datetime).label("dropoff_datetime"),
        nyctaxi.c.total_amount.label('fare'),
        ranked_fare,
        cast(percent_ranked_fare, FLOAT).label('percent_ranked_fare')
    ).where(
        nyctaxi.c.passenger_count == 3,
        nyctaxi.c.pickup_datetime >= '2015-01-11',
        nyctaxi.c.pickup_datetime < '2015-01-12'
    ).order_by(
        nyctaxi.c.vendor_id,
        nyctaxi.c.pickup_datetime
    )

    # Compile the query
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(query)
    print_data("Window Function - Ranking", compiled_query, result)


def select_window_first_value(conn):
    """
    Generates equivalent SQL to (Window FIRST_VALUE Example):

        SELECT
            vendor_id,
            pickup_datetime,
            tip_amount,
            tip_amount -
                FIRST_VALUE(tip_amount) IGNORE NULLS OVER
                    (PARTITION BY vendor_id ORDER BY tip_amount) AS lowest_amount,
            tip_amount -
                DECIMAL
                (
                    AVG(tip_amount) OVER
                        (
                            PARTITION BY vendor_id
                            ORDER BY tip_amount
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                        )
                ) AS average_amount,
            tip_amount -
                FIRST_VALUE(tip_amount) IGNORE NULLS OVER
                    (PARTITION BY vendor_id ORDER BY tip_amount DESC) AS highest_amount
        FROM demo.nyctaxi
        WHERE
            passenger_count = 5 AND
            pickup_datetime >= '2015-04-17' AND pickup_datetime < '2015-04-18' AND
            tip_amount > 0 AND
            trip_distance > 0
        ORDER BY
            vendor_id,
            pickup_datetime

    See:  https://docs.kinetica.com/7.2/sql/query/#window

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    nyctaxi = Table('nyctaxi', metadata, autoload_with = conn, schema = 'demo')

    # Alias for convenience
    tip_amount = nyctaxi.c.tip_amount

    # Define the window function components
    lowest_amount = tip_amount - FirstValue(tip_amount, ignore_nulls = True).over(
        partition_by = nyctaxi.c.vendor_id,
        order_by = tip_amount,
    )

    average_amount = tip_amount - func.decimal(
        func.avg(tip_amount).over(
            partition_by = nyctaxi.c.vendor_id,
            order_by = tip_amount,
            rows = (None, None)
        )
    )

    highest_amount = tip_amount - FirstValue(tip_amount, ignore_nulls = True).over(
        partition_by = nyctaxi.c.vendor_id,
        order_by = desc(tip_amount),
    )

    # Build the select statement
    query = select(
        nyctaxi.c.vendor_id,
        func.datetime(nyctaxi.c.pickup_datetime).label("pickup_datetime"),
        tip_amount,
        lowest_amount.label('lowest_amount'),
        average_amount.label('average_amount'),
        highest_amount.label('highest_amount')
    ).where(
        (nyctaxi.c.passenger_count == 5) &
        (nyctaxi.c.pickup_datetime >= '2015-04-17') &
        (nyctaxi.c.pickup_datetime < '2015-04-18') &
        (nyctaxi.c.tip_amount > 0) &
        (nyctaxi.c.trip_distance > 0)
    ).order_by(
        nyctaxi.c.vendor_id,
        nyctaxi.c.pickup_datetime
    )

    # Compile the query
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(query)
    print_data("Window Function - First Value", compiled_query, result)


def select_window_ntile(conn):
    """
    Generates equivalent SQL to (Window N-Tile Example):

        SELECT
            vendor_id,
            DECIMAL(AVG(total_amount)) AS average_total_amount,
            DECIMAL(AVG(IF(quartile IN (2,3), total_amount, null))) AS average_interq_range_total_amount
        FROM
        (
            SELECT
                vendor_id,
                total_amount,
                NTILE(4) OVER (PARTITION BY vendor_id ORDER BY total_amount) quartile
            FROM
                demo.nyctaxi
        )
        GROUP BY vendor_id
        ORDER BY vendor_id

    See:  https://docs.kinetica.com/7.2/sql/query/#window

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    nyctaxi = Table('nyctaxi', metadata, autoload_with = conn, schema = 'demo')

    # NTILE window function to calculate quartile
    quartile_subquery = select(
        nyctaxi.c.vendor_id,
        nyctaxi.c.total_amount,
        func.ntile(4).over(
            partition_by = nyctaxi.c.vendor_id,
            order_by = nyctaxi.c.total_amount
        ).label('quartile')
    ).subquery()

    # Calculate average total amount and average interquartile range total amount
    query = select(
        quartile_subquery.c.vendor_id,
        func.decimal(func.avg(quartile_subquery.c.total_amount)).label('average_total_amount'),
        func.decimal(
            func.avg(
                case(
                    (quartile_subquery.c.quartile.in_([2, 3]), quartile_subquery.c.total_amount),
                    else_ = None
                )
            )
        ).label('average_interq_range_total_amount')
    ).group_by(
        quartile_subquery.c.vendor_id
    ).order_by(
        quartile_subquery.c.vendor_id
    )

    # Compile the query
    compiled_query = query.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(compiled_query)
    print_data("Window Function - N-Tile", compiled_query, result)


def select_pivot(conn, schema):
    """
    Generates equivalent SQL to (PIVOT Example):

        SELECT
            name,
            Home_Phone,
            Work_Phone,
            Cell_Phone
        FROM
            phone_list
        PIVOT
        (
            MAX(phone_number) AS Phone
            FOR phone_type IN ('Home', 'Work', 'Cell')
        )

    See:  https://docs.kinetica.com/7.2/sql/query/#pivot

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """

    metadata = MetaData()

    # Create a handle to the source table
    phone_list = Table('phone_list', metadata, autoload_with = conn, schema = schema)

    # Define the aggregate expressions and pivot details
    aggregate_expressions = [(func.max(column("phone_number")), 'Phone')]
    pivot_column = column("phone_type")
    pivot_values = ['Home', 'Work', 'Cell']

    # Create the Pivot object
    query = (
        PivotSelect(
            column("name"),
            column("Home_Phone"),
            column("Work_Phone"),
            column("Cell_Phone")
        )
        .select_from(phone_list)
        .pivot("max(phone_number) AS Phone", "phone_type", ["'Home'", "'Work'", "'Cell'"])
        .order_by(column("name"))
    )

    # Compile the query
    compiled_query = query.compile(conn)

    result = conn.execute(compiled_query)
    print_data("Pivot", compiled_query, result)



    # Quoting the table name for consistency here; only the user-defined schema may need it
    new_table_name = f"""{'"' + schema + '".' if schema else ''}"customer_contact_from_pivot" """

    # Create a new table using the query for the UNPIVOT example, next
    create_stmt = CreateTableAs(
            new_table_name,
            query
    ).compile(conn)

    conn.execute(create_stmt)


def select_unpivot(conn, schema):
    """
    Generates equivalent SQL to (UNPIVOT Example):

        SELECT name, phone_type, phone_number
        FROM
        (
            SELECT
                name,
                Home_Phone AS Home,
                Work_Phone AS Work,
                Cell_Phone AS Cell
            FROM
                customer_contact
        )
        UNPIVOT (phone_number FOR phone_type IN (Home, Work, Cell))
        ORDER BY name, phone_type

    See:  https://docs.kinetica.com/7.2/sql/query/#unpivot

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """

    metadata = MetaData()

    # Create a handle to the source table
    customer_contact = Table('customer_contact', metadata, autoload_with = conn, schema = schema).alias("cc")

    # Create the subquery (as an alias)
    subquery = select(
        customer_contact.c.name,
        customer_contact.c.home_phone.label('Home'),
        customer_contact.c.work_phone.label('Work'),
        customer_contact.c.cell_phone.label('Cell')
    )

    query = (
        UnpivotSelect(column("name"), column("phone_type"), column("phone_number"))
        .select_from(subquery)
        .unpivot("phone_number", "phone_type", ["Home", "Work", "Cell"])
        .order_by(column("name"), column("phone_type"))
    )

    # Compile the query
    compiled_query = query.compile(conn)

    result = conn.execute(compiled_query)
    print_data("Unpivot", compiled_query, result)


def select_union(conn, schema):
    """
    Generates equivalent SQL to (UNION Example):

        SELECT
            food_name,
            category,
            price
        FROM
            lunch_menu
        UNION
        SELECT
            food_name,
            category,
            price
        FROM
            dinner_menu
        ORDER BY
            food_name,
            category,
            price

    See:  https://docs.kinetica.com/7.2/sql/query/#union

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """

    metadata = MetaData()

    # Create handles to the source tables
    dinner_menu = Table('dinner_menu', metadata, autoload_with = conn, schema = schema).alias('dm')
    lunch_menu = Table('lunch_menu', metadata, autoload_with = conn, schema = schema).alias('lm')

    # Create the Select statements
    lunch_select = select(lunch_menu.c.food_name, lunch_menu.c.category, lunch_menu.c.price)
    dinner_select = select(dinner_menu.c.food_name, dinner_menu.c.category, dinner_menu.c.price)

    # Create the union query
    union_query = union(lunch_select, dinner_select).order_by("food_name", "category", "price")

    # Compile the query
    compiled_query = union_query.compile(conn)

    result = conn.execute(compiled_query)
    print_data("Set Union (Deduplicate)", compiled_query, result)


def select_union_all(conn, schema):
    """
    Generates equivalent SQL to (UNION ALL Example):

        SELECT
            food_name,
            category,
            price
        FROM
            lunch_menu
        UNION ALL
        SELECT
            food_name,
            category,
            price
        FROM
            dinner_menu
        ORDER BY
            food_name,
            category,
            price

    See:  https://docs.kinetica.com/7.2/sql/query/#union

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """

    metadata = MetaData()

    # Create handles to the source tables
    dinner_menu = Table('dinner_menu', metadata, autoload_with = conn, schema = schema).alias('dm')
    lunch_menu = Table('lunch_menu', metadata, autoload_with = conn, schema = schema).alias('lm')

    # Create the Select statements
    lunch_select = select(lunch_menu.c.food_name, lunch_menu.c.category, lunch_menu.c.price)
    dinner_select = select(dinner_menu.c.food_name, dinner_menu.c.category, dinner_menu.c.price)

    # Create the union all query
    union_query = union_all(lunch_select, dinner_select).order_by("food_name", "category", "price")

    # Compile the query
    compiled_query = union_query.compile(conn)

    result = conn.execute(compiled_query)
    print_data("Set Union (Keep Duplicates)", compiled_query, result)


def select_intersect(conn, schema):
    """
    Generates equivalent SQL to (INTERSECT Example):

        SELECT
            food_name,
            category,
            price
        FROM
            lunch_menu
        INTERSECT
        SELECT
            food_name,
            category,
            price
        FROM
            dinner_menu
        ORDER BY
            food_name,
            category,
            price

    See:  https://docs.kinetica.com/7.2/sql/query/#intersect

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """

    metadata = MetaData()

    # Create handles to the source tables
    dinner_menu = Table('dinner_menu', metadata, autoload_with = conn, schema = schema).alias('dm')
    lunch_menu = Table('lunch_menu', metadata, autoload_with = conn, schema = schema).alias('lm')

    # Create the Select statements
    lunch_select = select(lunch_menu.c.food_name, lunch_menu.c.category, lunch_menu.c.price)
    dinner_select = select(dinner_menu.c.food_name, dinner_menu.c.category, dinner_menu.c.price)

    # Create the intersect query
    intersect_query = intersect(lunch_select, dinner_select).order_by("food_name", "category", "price")

    # Compile the query
    compiled_query = intersect_query.compile(conn)

    result = conn.execute(compiled_query)
    print_data("Set Intersection", compiled_query, result)


def select_except(conn, schema):
    """
    Generates equivalent SQL to (EXCEPT Example):

        SELECT
            food_name,
            category,
            price
        FROM
            lunch_menu
        EXCEPT
        SELECT
            food_name,
            category,
            price
        FROM
            dinner_menu
        ORDER BY
            food_name,
            category,
            price

    See:  https://docs.kinetica.com/7.2/sql/query/#except

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """

    metadata = MetaData()

    # Create handles to the source tables
    dinner_menu = Table('dinner_menu', metadata, autoload_with = conn, schema = schema).alias('dm')
    lunch_menu = Table('lunch_menu', metadata, autoload_with = conn, schema = schema).alias('lm')

    # Create the Select statements
    lunch_select = select(lunch_menu.c.food_name, lunch_menu.c.category, lunch_menu.c.price)
    dinner_select = select(dinner_menu.c.food_name, dinner_menu.c.category, dinner_menu.c.price)

    # Create the except query
    except_query = except_(lunch_select, dinner_select).order_by("food_name", "category", "price")

    # Compile the query
    compiled_query = except_query.compile(conn)

    result = conn.execute(compiled_query)
    print_data("Set Subtraction", compiled_query, result)


def table_function_filter_by_string(conn, schema):
    """
    Generates equivalent SQL to (FILTER_BY_STRING Example):

        SELECT *
        FROM TABLE
        (
            FILTER_BY_STRING
            (
                TABLE_NAME => INPUT_TABLE(SELECT event_time, message FROM event_log),
                COLUMN_NAMES => 'message',
                MODE => 'contains',
                EXPRESSION => 'ERROR'
            )
        )

    See:  https://docs.kinetica.com/7.2/sql/query/#filter-by-string

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the source table
    input_table = Table('event_log', metadata, autoload_with = conn, schema = schema)

    # Create an instance of your custom FilterByString function
    filter_by_str_func = FilterByString(
        table_name = select(column('event_time'), column('message')).select_from(text(input_table.fullname)),
        column_names = 'message',
        mode = 'contains',
        expression = 'ERROR',
        # options = {'OPTION1': 'VALUE1', 'OPTION2': 'VALUE2'}
    )

    compiled_filter_by_str = filter_by_str_func.compile(conn, compile_kwargs = {"literal_binds": True})

    result = conn.execute(compiled_filter_by_str)
    print_data("Filter by String", compiled_filter_by_str, result)


def ml_evaluate_model_select(conn, schema):
    """
    Generates equivalent SQL to (EVALUATE_MODEL Table Function Example):

        SELECT * FROM TABLE
        (
            EVALUATE_MODEL
            (
                MODEL => 'raster_model',
                DEPLOYMENT_MODE => 'batch',
                REPLICATIONS =>1,
                SOURCE_TABLE => INPUT_TABLE(select raster_uri from raster_input)
            )
        )
    
    See:  https://docs.kinetica.com/7.2/sql/ml/#evaluate-model

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    source_table = select(column("raster_uri")).select_from(text(f"{schema + '.' if schema else ''}raster_input")).compile(conn)

    stmt = EvaluateModel(
        model = 'raster_model',
        deployment_mode = 'batch',
        replications = 1,
        source_table = source_table
    )

    compiled_stmt = stmt.compile(conn, compile_kwargs = {"literal_binds": True})

    print_statement("Evaluate Model - SELECT", compiled_stmt)


def ml_evaluate_model_execute(conn, schema):
    """
    Generates equivalent SQL to (EVALUATE_MODEL Table Function Example):

        EXECUTE FUNCTION EVALUATE_MODEL
        (
            MODEL => 'raster_model',
            DEPLOYMENT_MODE => 'batch',
            REPLICATIONS =>1,
            SOURCE_TABLE => INPUT_TABLE(select raster_uri from raster_input),
            DESTINATION_TABLE => 'raster_output'
        )

    See:  https://docs.kinetica.com/7.2/sql/ml/#evaluate-model

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    source_table = select(column("raster_uri")).select_from(text(f"{schema + '.' if schema else ''}raster_input")).compile(conn)

    stmt = EvaluateModel(
        model = 'raster_model',
        deployment_mode = 'batch',
        replications = 1,
        source_table = source_table,
        destination_table = f"{schema + '.' if schema else ''}raster_output"
    )

    compiled_stmt = stmt.compile(conn, compile_kwargs = {"literal_binds": True})

    print_statement("Evaluate Model - EXECUTE", compiled_stmt)


def update_with_subquery(conn, schema):
    """
    Generates equivalent SQL to (UPDATE with Subquery in WHERE Clause Example):

        UPDATE employee b
        SET sal = sal * 1.05
        WHERE sal =
        (
            SELECT MIN(sal)
            FROM employee l
            WHERE b.dept_id = l.dept_id
        )

    See:  https://docs.kinetica.com/7.2/sql/dml/#update

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the lookup table
    e_lookup = Table('employee', metadata, autoload_with = conn, schema = schema)

    # Create an alias for the base table being updated
    e_base = alias(e_lookup, name = "b")

    # Subquery to find the MIN(sal) for each department
    min_sal_in_dept = (
        select(func.min(e_lookup.c.sal))
        .where(e_base.c.dept_id == e_lookup.c.dept_id)
        .scalar_subquery()
    )

    # Update statement
    stmt = (
        update(e_base)
        .where(e_base.c.sal == min_sal_in_dept)
        .values(sal = e_base.c.sal * 1.05)
    )

    # Compile to SQL to see the query
    compiled_query = stmt.compile(conn)

    # Print the generated SQL query
    print_statement("Update with Subquery", compiled_query)

    check_data("Update with Subquery Data (Before)", metadata, conn, schema, 'employee', 'id')

    conn.execute(compiled_query)

    check_data("Update with Subquery Data (After)", metadata, conn, schema, 'employee', 'id')


def update_with_subquery_in_set_clause(conn, schema):
    """
    Generates equivalent SQL to (UPDATE with Subquery in SET Clause Example):

        UPDATE  employee b
        SET     sal =
                (
                    SELECT MAX(sal)
                    FROM employee l
                    WHERE l.dept_id = b.dept_id
                ) * .1 + sal * .9

    See:  https://docs.kinetica.com/7.2/sql/dml/#update

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create a handle to the lookup table
    e_lookup = Table('employee', metadata, autoload_with = conn, schema = schema)

    # Create an alias for the base table being updated
    e_base = alias(e_lookup, name = "b")

    # Subquery to find the MAX(sal) for each department
    max_sal_in_dept = (
        select(func.max(e_lookup.c.sal))
        .where(e_base.c.dept_id == e_lookup.c.dept_id)
        .scalar_subquery()
    )

    # Update statement
    stmt = (
        update(e_base)
        .values(sal = max_sal_in_dept * .1 + e_base.c.sal * .9)
    )

    # Compile to SQL to see the query
    compiled_query = stmt.compile(conn)

    # Print the generated SQL query
    print_statement("Update with Subquery in SET Clause", compiled_query)

    check_data("Update with Subquery in SET Clause Data (Before)", metadata, conn, schema, 'employee', 'id')

    conn.execute(compiled_query)

    check_data("Update with Subquery in SET Clause Data (After)", metadata, conn, schema, 'employee', 'id')


def update_with_join_infixed(conn, schema):
    """
    Generates equivalent SQL to (UPDATE with Infixed JOIN Clause Example):

        UPDATE eb
        SET sal = e.salary, manager_id = e.manager_id
        FROM employee_backup eb
        JOIN employee e ON eb.id = e.id

    See:  https://docs.kinetica.com/7.2/sql/dml/#update

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create handles to the source & target tables
    employee = Table('employee', metadata, autoload_with = conn, schema = schema)
    employee_backup = Table('employee_backup', metadata, autoload_with = conn, schema = schema)

    update_stmt = KiUpdate(
        employee_backup,
        from_table = employee,
        join_condition = employee_backup.c.id == employee.c.id,
    ).values(
        sal = employee.c.sal,
        manager_id = employee.c.manager_id
    )

    # Compile to see the generated SQL query
    update_stmt = update_stmt.compile(conn)


    # Print the generated SQL query
    print_statement("Update with Join (Infixed)", update_stmt)

    check_data("Update with Join (Infixed) Data (Before)", metadata, conn, schema, 'employee_backup', 'id')

    # Update a manager to be reflected in the update-with-join statement
    conn.execute(employee.update().where(employee.c.id==5).values(manager_id=1).compile(conn))

    conn.execute(update_stmt)

    check_data("Update with Join (Infixed) Data (After)", metadata, conn, schema, 'employee_backup', 'id')


def update_with_join_non_infixed(conn, schema):
    """
    Generates equivalent SQL to (UPDATE with Non-Infixed JOIN Clause Example):

        UPDATE  eb
        SET     sal = e.sal, manager_id = e.manager_id
        FROM    employee_backup eb, employee e
        WHERE   eb.id = e.id
    
    See:  https://docs.kinetica.com/7.2/sql/dml/#update

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create handles to the source & target tables
    employee = Table('employee', metadata, autoload_with = conn, schema = schema)
    employee_backup = Table('employee_backup', metadata, autoload_with = conn, schema = schema)

    # Create the update statement with FROM clause
    update_stmt = KiUpdate(
        employee_backup,
        from_table = employee,
        where_condition = (employee_backup.c.id == employee.c.id)
    ).values(
        sal = employee.c.sal,
        manager_id = employee.c.manager_id
    )

    # Compile to see the generated SQL query
    update_stmt = update_stmt.compile(conn)


    # Print the generated SQL query
    print_statement("Update with Join (Non-Infixed)", update_stmt)

    check_data("Update with Join (Non-Infixed) Data (Before)", metadata, conn, schema, 'employee_backup', 'id')

    # Update a manager & salary to be reflected in the update-with-join statement
    conn.execute(employee.update().where(employee.c.id==5).values(manager_id=2, sal=70000).compile(conn))

    conn.execute(update_stmt)

    check_data("Update with Join (Non-Infixed) Data (After)", metadata, conn, schema, 'employee_backup', 'id')


def delete_with_subquery(conn, schema):
    """
    Generates equivalent SQL to (DELETE with Subquery Example):

        DELETE
        FROM employee b
        WHERE id =
            (
                SELECT MAX(l.id)
                FROM employee l
                WHERE b.dept_id = l.dept_id
            )

    See:  https://docs.kinetica.com/7.2/sql/dml/#delete

    Args:
        conn (Connection): a SQLAlchemy connection to Kinetica
        schema (str): database schema in which to perform operations
    """
    metadata = MetaData()

    # Create handles with aliases to the lookup & base tables
    e_base = Table('employee', metadata, autoload_with = conn, schema = schema).alias("b")
    e_lookup = Table('employee', metadata, autoload_with = conn, schema = schema).alias("l")

    max_id_in_dept = (
        select(func.max(e_lookup.c.id))
        .where(e_base.c.dept_id == e_lookup.c.dept_id)
    ).scalar_subquery()

    # Create the DELETE statement with the subquery in the WHERE clause
    delete_stmt = delete(e_base).where(e_base.c.id == max_id_in_dept)

    delete_stmt = delete_stmt.compile(conn)


    # Print the generated SQL query
    print_statement("Delete with Subquery", delete_stmt)

    check_data("Delete with Subquery Data (Before)", metadata, conn, schema, 'employee', 'id')

    conn.execute(delete_stmt)

    check_data("Delete with Subquery Data (After)", metadata, conn, schema, 'employee', 'id')


def drop_schema(conn, schema):
    conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))


def create_schema(conn, schema):
    conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))



if __name__ == "__main__":

    param_args = sys.argv[1:]

    param_url = param_args[0] if len(param_args) >= 1 else ENV_URL
    param_user = param_args[1] if len(param_args) >= 2 else ENV_USER
    param_pass = param_args[2] if len(param_args) >= 3 else ENV_PASS
    param_schema = param_args[3] if len(param_args) >= 4 else ENV_SCHEMA
    param_bypass_ssl_cert_check = param_args[4] if len(param_args) >= 5 else ENV_BYPASS_SSL_CERT_CHECK
    param_recreate_schema = param_args[5] if len(param_args) >= 6 else ENV_RECREATE_SCHEMA

    param_bypass_ssl_cert_check = str(param_bypass_ssl_cert_check).upper() in ["1", "TRUE"]
    param_recreate_schema = str(param_recreate_schema).upper() in ["1", "TRUE"]

    sa_engine = create_engine(
        "kinetica://",
        connect_args = {
            "url": param_url,
            "username": param_user,
            "password": param_pass,
            "bypass_ssl_cert_check": param_bypass_ssl_cert_check,
        }
    )

    with sa_engine.connect() as sa_conn:

        print_header("Kinetica SQLAlchemy Driver Example Suite Run Results")

        if param_schema:
            if param_recreate_schema:
                drop_schema(sa_conn, param_schema)
            create_schema(sa_conn, param_schema)

        create_table_all_types(sa_conn, param_schema)
        create_table_replicated(sa_conn, param_schema)
        create_table_sharded_with_options(sa_conn, param_schema)
        create_table_as(sa_conn, param_schema)
        create_datasource(sa_conn, param_schema, param_url, param_user, param_pass)
        create_external_table(sa_conn, param_schema)

        create_example_tables(sa_conn, param_schema)

        insert_multiple_records(sa_conn, param_schema)
        insert_from_select(sa_conn, param_schema)
        insert_with_cte(sa_conn, param_schema)

        select_with_cte(sa_conn, param_schema)

        select_join_infixed(sa_conn, param_schema)
        select_join_non_infixed(sa_conn, param_schema)
        select_join_asof(sa_conn, param_schema)
        select_join_asof_filter(sa_conn, param_schema)

        if check_table(sa_conn, "demo", "nyctaxi"):
            select_aggregation_without_groupby(sa_conn)
            select_aggregation_with_groupby(sa_conn)
        if check_table(sa_conn, "demo", "stocks"):
            select_aggregation_rollup(sa_conn)
            select_aggregation_cube(sa_conn)
            select_aggregation_grouping_sets(sa_conn)

        if check_table(sa_conn, "demo", "nyctaxi"):
            select_window_rolling_sum(sa_conn)
            select_window_moving_average(sa_conn)
            select_window_ranking(sa_conn)
            select_window_first_value(sa_conn)
            select_window_ntile(sa_conn)

        select_pivot(sa_conn, param_schema)
        select_unpivot(sa_conn, param_schema)

        select_union(sa_conn, param_schema)
        select_union_all(sa_conn, param_schema)
        select_intersect(sa_conn, param_schema)
        select_except(sa_conn, param_schema)

        table_function_filter_by_string(sa_conn, param_schema)

        ml_evaluate_model_select(sa_conn, param_schema)
        ml_evaluate_model_execute(sa_conn, param_schema)

        update_with_subquery(sa_conn, param_schema)
        update_with_subquery_in_set_clause(sa_conn, param_schema)
        update_with_join_infixed(sa_conn, param_schema)
        update_with_join_non_infixed(sa_conn, param_schema)
        delete_with_subquery(sa_conn, param_schema)
