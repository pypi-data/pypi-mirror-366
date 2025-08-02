"""Kinetica types."""

from __future__ import annotations

import ipaddress
import json
import struct

import geojson
from shapely import wkt, GEOSException
from sqlalchemy import types as sqltypes, TypeDecorator, ARRAY, BigInteger, String, LargeBinary, DECIMAL
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.type_api import UserDefinedType




class Character(sqltypes.String):
    __visit_name__ = "Character"

    def __init__(self, length: int | None = None, collation: str | None = None) -> None:
        super().__init__(length, collation)

class CHARACTER(Character):
    __visit_name__ = "CHARACTER"


class DATE(sqltypes.DATE):
    pass


class DATETIME(sqltypes.DATETIME):
    pass


class TIME(sqltypes.TIME):
    pass


class TIMESTAMP(sqltypes.INT):
    pass


class TINYINT(sqltypes.SMALLINT):
    __visit_name__ = "TINYINT"

class Tinyint(sqltypes.SMALLINT):
    pass

class SMALLINT(sqltypes.SMALLINT):
    __visit_name__ = "SMALLINT"

class Smallint(sqltypes.SMALLINT):
    __visit_name__ = "SMALLINT"


class INTEGER(sqltypes.INTEGER):
    pass


class BIGINT(sqltypes.BIGINT):
    pass

class Bigint(BIGINT):
    pass


class DECIMAL(TypeDecorator):  # type:ignore[type-arg]
    # Use the DECIMAL type as the base type
    impl = DECIMAL
    __visit_name__ = "DECIMAL"
    cache_ok = False

    def process_bind_param(self, value, dialect):
        return float(value) if value else None
    # Override process_result_value to convert string to float
    def process_result_value(self, value, dialect):
        # Convert the string from the database to a float
        if value is not None:
            return float(value)
        return None

class Numeric(sqltypes.NUMERIC):
    # __visit_name__ = "Numeric"
    pass

class numeric(sqltypes.NUMERIC):
    pass

class NUMERIC(sqltypes.NUMERIC):
    pass

class REAL(sqltypes.REAL):  # type:ignore[type-arg]
    pass

class Real(sqltypes.REAL):  # type:ignore[type-arg]
    pass

class DOUBLE(sqltypes.DOUBLE):  # type:ignore[valid-type,misc]
    pass


class FLOAT(sqltypes.FLOAT):  # type:ignore[type-arg]
    pass


class BOOLEAN(sqltypes.BOOLEAN):
    pass


class VARCHAR(sqltypes.VARCHAR):
    pass


class CHAR(sqltypes.CHAR):
    pass


class BLOB(TypeDecorator):
    impl = String  # Use String as the implementation type
    cache_ok = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: Define any custom parameters or default values here

    def process_result_value(self, value, dialect):
        if value is not None:
            # Convert bytes back to string when retrieving
            return value.decode('utf-8')
        return value


@compiles(BLOB, 'kinetica')
def compile_blob_kinetica(type_, compiler, **kw):
    return "BLOB"


class JSONArray(TypeDecorator):
    impl = VARCHAR
    cache_ok = False

    def __init__(self, size=None):
        self.size = size
        super().__init__()

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)

    def copy(self, **kwargs):
        return JSONArray(self.size)


@compiles(JSONArray)
def compile_jsonarray(type_, compiler, **kw):
    if type_.size is None:
        return "JSON"
    else:
        return f"JSON[{type_.size}]"


class JSON(sqltypes.JSON):
    def bind_processor(self, dialect):
        # Return a function that processes the value before storing it in the database
        def process(value):
            if value is None:
                return value
            return json.dumps(value)

        return process

    def result_processor(self, dialect, coltype):
        # Return a function that processes the value after retrieving it from the database
        def process(value):
            if value is None:
                return value
            return json.loads(value)

        return process


@compiles(ARRAY, 'kinetica')
def compile_array(element, compiler, **kw):
    return f"{element.item_type}[{element.dimensions}]" if element.dimensions else f"{element.item_type}[]"


class IPV4(TypeDecorator):
    impl = String
    cache_ok = False

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(String(15))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, ipaddress.IPv4Address):
            return str(value)
        return str(ipaddress.IPv4Address(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return ipaddress.IPv4Address(value)


@compiles(IPV4, 'kinetica')
def compile_ipv4_kinetica(type_, compiler, **kw):
    return "IPV4"


class UnsignedBigInteger(TypeDecorator):
    impl = BigInteger
    cache_ok = False

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(BigInteger)

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return value


@compiles(UnsignedBigInteger, 'kinetica')
def compile_unsigned_bigint_kinetica(type_, compiler, **kw):
    return "UNSIGNED BIGINT"


class VECTOR(UserDefinedType):
    cache_ok = False

    def __init__(self, dimension):
        self.dimension = dimension

    def get_col_spec(self):
        return f"VECTOR({self.dimension})"

    def bind_processor(self, dialect):
        def process(value):
            if isinstance(value, list):
                converted_value = f'{[float(num) if isinstance(num, int) else num for num in value]}'
                return converted_value
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value:
                converted_column_value = bytes(','.join(
                    str(e) for e in [*struct.unpack("%sf" % self.dimension, value)]), 'utf-8'
                )
                return converted_column_value
            return value
        return process


@compiles(VECTOR)
def compile_vector(element, compiler, **kw):
    return f"VECTOR({element.dimension})"


class Vector(VECTOR):
    pass

class vector(VECTOR):
    pass


class BlobWKT(TypeDecorator):
    impl = String
    cache_ok = False

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        from shapely import wkb
        if isinstance(value, str):
            try:
                # convert hex binary string to geometry
                wkb_data = bytes.fromhex(value.replace('0x', ''))
                geom = wkb.loads(wkb_data)
                return f'{str(geom)}'
            except Exception as e:
                # valid geometry string, pass on as is
                return value


    def process_result_value(self, value, dialect):
        return f"0x{value.hex()}" if value else None


@compiles(BlobWKT, "kinetica")
def compile_blobwkt(element, compiler, **kw):
    return "BLOB(WKT)"


class GEOMETRY(TypeDecorator):
    impl = String
    cache_ok = False

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(String())  # Adjust size as needed

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        # Ensure the value is a WKT string
        if isinstance(value, str):
            # Validate the WKT by loading it using shapely
            geom = wkt.loads(value)
            return wkt.dumps(geom)
        raise ValueError("Invalid WKT value")

    def process_result_value(self, value, dialect):
        # Return the WKT string as it is
        return value


@compiles(GEOMETRY)
def compile_geometry(element, compiler, **kw):
    return "GEOMETRY"

class Geometry(GEOMETRY):
    pass


__all__ = (
    "BIGINT",
    "BLOB",
    "BlobWKT",
    "BOOLEAN",
    "CHAR",
    "DATE",
    "DECIMAL",
    "DOUBLE",
    "FLOAT",
    "GEOMETRY",
    "Geometry",
    "INTEGER",
    "IPV4",
    "JSON",
    "JSONArray",
    "REAL",
    "SMALLINT",
    "TIME",
    "TIMESTAMP",
    "TINYINT",
    "UnsignedBigInteger",
    "VARCHAR",
    "VECTOR",
    "Vector",
)
