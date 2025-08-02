import logging
import os
import sys
from sqlalchemy import create_engine, text

ENV_URL = os.getenv('PY_TEST_URL', 'http://localhost:9191')
ENV_USER = os.getenv('PY_TEST_USER', "")
ENV_PASS = os.getenv('PY_TEST_PASS', "")
ENV_SCHEMA = os.getenv('PY_TEST_SCHEMA', 'sqlalchemy')
ENV_BYPASS_SSL_CERT_CHECK = os.getenv('PY_TEST_BYPASS_CERT_CHECK', True)



def get_engine(url, username, password, bypass_ssl_cert_check):
    """ This connects to a Kinetica database and returns a SQLAlchemy engine,
        which will be used to execute subsequent SQL commands.

    Args:
        url: Kinetica URL to connect to
        username: account name to log in as
        password: account password to log in with
        bypass_ssl_cert_check: whether to bypass the certificate validity check
            when connecting to Kinetica over HTTPS

    Returns:
        SQLAlchemy engine object
    """


    engine = create_engine(
        "kinetica://",
        connect_args = {
                "url": url,
                "username": username,
                "password": password,
                "bypass_ssl_cert_check": bypass_ssl_cert_check,
        },
    )

    # Test engine's connectivity
    with engine.connect() as conn:
        conn.execute(text("SELECT 1 FROM ITER"))

    return engine


def execute_sql_literals(engine, schema):
    """ This method demonstrates using the SQLAlchemy engine to execute literal
        SQL statements on the Kinetica database.

    Args:
        engine: SQLAlchemy engine object
        schema: name of the schema in which to create example objects
    """


    # Create schema, if necessary
    with engine.connect() as conn:
        if schema:
            print(f"\nEnsuring schema [{schema}] exists...")
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

    # Create a table prefix for the schema, if necessary
    schema_prefix = "" if not schema else schema + "."
    table_name = "column_types"



    SQL_CREATE_TABLE = f"""
        CREATE OR REPLACE TABLE {schema_prefix}{table_name}
        (
            "boolean"          BOOLEAN,          /* native boolean            */
            "tinyint"          TINYINT,          /* native int8               */
            "smallint"         SMALLINT,         /* native int16              */
            "integer"          INTEGER,          /* native integer            */
            "bigint"           BIGINT,           /* native long               */
            "unsigned_bigint"  UNSIGNED BIGINT,  /* native unsigned long      */
            "real"             REAL,             /* native float              */
            "double"           DOUBLE,           /* native double             */
            "string"           VARCHAR,          /* native string             */
            "char1"            VARCHAR(1),       /* native char1              */
            "char256"          VARCHAR(256),     /* native char256            */
            "decimal"          DECIMAL(10,4),    /* native decimal            */
            "ipv4"             IPV4,             /* native ipv4               */
            "uuid"             UUID,             /* native uuid               */
            "date"             DATE,             /* native date               */
            "time"             TIME,             /* native time               */
            "timestamp"        TIMESTAMP,        /* native timestamp          */
            "datetime"         DATETIME,         /* native datetime           */
            "blob"             BLOB,             /* native bytes              */
            "blob_wkt"         BLOB(WKT),        /* native wkt (bytes)        */
            "geometry"         GEOMETRY,         /* native wkt (string)       */
            "json"             JSON,             /* native JSON               */
            "v1"               VECTOR(1),        /* 1-item vector             */
            "v10"              VECTOR(10),       /* 10-item vector            */
            "a1_boolean"       BOOLEAN[1],       /* 1-item boolean array      */
            "a10_boolean"      BOOLEAN[10],      /* 10-item boolean array     */
            "a1_integer"       INTEGER[1],       /* 1-item int array          */
            "a10_integer"      INTEGER[10],      /* 10-item int array         */
            "a1_bigint"        BIGINT[1],        /* 1-item long array         */
            "a10_bigint"       BIGINT[10],       /* 10-item long array        */
            "a1_real"          REAL[1],          /* 1-item float array        */
            "a10_real"         REAL[10],         /* 10-item float array       */
            "a1_double"        DOUBLE[1],        /* 1-item double array       */
            "a10_double"       DOUBLE[10],       /* 10-item double array      */
            "a1_varchar"       VARCHAR[1],       /* 1-item string array       */
            "a10_varchar"      VARCHAR[10],      /* 10-item string array      */
            "a1_json"          JSON[1],          /* 1-item JSON array         */
            "a10_json"         JSON[10]          /* 10-item JSON array        */
        )
    """

    # Create an example table with various data types, using automatic
    # connection management
    with engine.connect() as conn:
        print(f"\nCreating table [{schema_prefix}{table_name}]...")
        conn.execute(text(SQL_CREATE_TABLE))



    SQL_SELECT = f"""
        SELECT
            column_name AS Column_Name,
            name AS Kinetica_Type,
            sql_typename AS SQL_Type,
            DECODE(is_nullable,0,'NOT NULLABLE',1,'NULLABLE') AS Is_Nullable,
            size AS Data_Size,
            prec AS "Precision",
            scale AS Scale
        FROM ki_catalog.ki_columns c
        JOIN ki_catalog.ki_datatypes t ON c.column_type_oid = t.oid
        WHERE schema_name = '{schema}' AND table_name = '{table_name}'
        ORDER BY column_position
    """
    
    # Execute query with a new connection, using manual connection management
    conn = engine.connect()
    result1 = conn.execute(text(SQL_SELECT))

    print(f"\nColumns of table [{schema_prefix}{table_name}]:")
    print_data(result1, column_widths = [15, 13, 27, 11, 9, 9, 5])



    SQL_INSERT = f"""
        INSERT INTO {schema_prefix}{table_name} ("integer", char256, "real", "double")
        VALUES (1, 'str1', 30.456, 123643543.4576)
    """

    # Insert data into target table with previous connection
    print(f"\nInserting data into table [{schema_prefix}{table_name}]...")
    conn.execute(text(SQL_INSERT))



    # Query target table with previous connection
    result2 = conn.execute(text(f"""SELECT "integer", char256, "real", "double" FROM {schema_prefix}{table_name}"""))

    print(f"\nData in table [{schema_prefix}{table_name}]:")
    print_data(result2, column_widths = [7, 7, 20, 20])


    conn.close()


def print_data(result, column_widths):
    
    columns = [column for column in result._metadata.keys]

    # Column headers
    print(" ".join([f"{columns[i]:{column_widths[i]}}" for i in range(len(columns))]))
    print(" ".join([f"{'-'*column_widths[i]:{column_widths[i]}}" for i in range(len(columns))]))

    # Column values
    for row in result:
        print(" ".join([f"{row[i]:{column_widths[i]}}" for i in range(len(row))]))



if __name__ == "__main__":
    args = sys.argv[1:]

    url = args[0] if len(args) >= 1 else ENV_URL
    username = args[1] if len(args) >= 2 else ENV_USER
    password = args[2] if len(args) >= 3 else ENV_PASS
    schema = args[3] if len(args) >= 4 else ENV_SCHEMA
    bypass_ssl_cert_check = args[4] if len(args) >= 5 else ENV_BYPASS_SSL_CERT_CHECK

    bypass_ssl_cert_check = str(bypass_ssl_cert_check).upper() in ["1", "TRUE"]

    engine = get_engine(url, username, password, bypass_ssl_cert_check)
    
    execute_sql_literals(engine, schema)
