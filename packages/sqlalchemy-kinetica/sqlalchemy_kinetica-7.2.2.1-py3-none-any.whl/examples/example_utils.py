import json
import string
from decimal import getcontext, Decimal
import uuid
import random
from typing import Type, Any

from faker import Faker
from shapely.geometry import Point, LineString, Polygon

from sqlalchemy import (column, select, Table)
from sqlalchemy_kinetica.dialect import KineticaDialect

__all__ = [
    "fake",
    "generate_random_value",
    "generate_list_of_type",
    "generate_random_vector",
    "generate_random_json",
    "generate_random_unicode_string",
    "generate_random_utf8_blob",
    "generate_random_decimal",
    "generate_random_alphanumeric_string",
    "generate_random_point",
    "generate_random_linestring",
    "generate_random_polygon",
    "generate_random_record",
    "print_header",
    "print_statement",
    "print_data",
    "check_data",
    "check_table"
]

# Create a Faker instance
fake = Faker()


# Data generation methods
def generate_random_value(value_type: Type) -> Any:
    if value_type == int:
        return random.randint(0, 100)
    elif value_type == float:
        return random.uniform(0, 100)
    elif value_type == str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=10))
    elif value_type == bool:
        return random.choice([True, False])
    else:
        raise ValueError(f"Unsupported type: {value_type}")


def generate_list_of_type(value_type: Type, num_elements: int) -> str:
    return f"{[generate_random_value(value_type) for _ in range(num_elements)]}"


def generate_random_vector(size=10):
    # Generate a vector of random floats
    vector = [random.random() for _ in range(size)]
    return f"{vector}"


def generate_random_json():
    # Create a dictionary with random data
    data = {
        "name": fake.name(),
        "email": fake.email(),
        # "dob": fake.date_of_birth().isoformat(),  # .strftime("%Y-%m-%d")
        "phone_number": fake.phone_number(),
        "ssn": fake.ssn(),
    }

    # Convert the dictionary to a JSON string
    json_string = json.dumps(data, default=str)
    return json_string


def generate_random_unicode_string(length):
    # Generate a random string of Unicode characters within the BMP
    return "".join(
        random.choice(string.ascii_letters + string.digits + string.punctuation + " ")
        for _ in range(length)
    )


def generate_random_utf8_blob(length):
    # Generate a random Unicode string
    random_unicode_string = generate_random_unicode_string(length)

    # Encode the string to UTF-8 bytes
    utf8_bytes = random_unicode_string.encode("utf-8")

    return f"0x{utf8_bytes.hex()}"


def generate_random_decimal(precision, scale):
    # Set the context for decimal to the desired precision
    getcontext().prec = precision

    # Calculate the maximum and minimum values based on precision and scale
    max_value = 10 ** (precision - scale) - 1
    min_value = -max_value

    # Generate a random integer within the range
    integer_part = random.randint(min_value, max_value)

    # Generate the fractional part
    fractional_part = random.randint(0, 10 ** scale - 1)

    # Combine the integer and fractional parts
    return Decimal(integer_part) + Decimal(fractional_part) / Decimal(10 ** scale)


# Function to generate a random string of letters and digits
def generate_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return "".join(random.choice(letters_and_digits) for _ in range(length))


def generate_random_point():
    x = random.uniform(-180, 180)
    y = random.uniform(-90, 90)
    point = Point(x, y)
    return point.wkt


def generate_random_linestring(num_points=5):
    points = [
        (random.uniform(-180, 180), random.uniform(-90, 90)) for _ in range(num_points)
    ]
    line = LineString(points)
    return line.wkt


def generate_random_polygon(num_points=5):
    points = [
        (random.uniform(-180, 180), random.uniform(-90, 90)) for _ in range(num_points)
    ]
    # Ensure the polygon is closed by repeating the first point
    points.append(points[0])
    polygon = Polygon(points)
    return polygon.wkt


def generate_random_record():
    return {
        "i": random.randint(0, 1000000),
        "ti": random.randint(0, 15),
        "si": random.randint(0, 250),
        "bi": random.randint(-9223372036854775808, 9223372036854775807),
        "ub": random.randint(0, 9223372036854775807),
        "b": random.randint(0, 1),
        "r": random.uniform(-100, 100),
        "d": random.uniform(-100, 100),
        "dc": generate_random_decimal(10, 4),
        "s": generate_random_alphanumeric_string(50),
        "cd": generate_random_alphanumeric_string(30),
        "ct": generate_random_alphanumeric_string(256),
        "ip": fake.ipv4(),
        "u": uuid.uuid4(),
        "td": fake.date_between().strftime("%Y-%m-%d"),
        "tt": str(fake.time_object()),
        "dt": fake.date_time_this_year().strftime("%Y-%m-%d"),
        "ts": int(fake.date_time_this_year().timestamp()),
        "j": generate_random_json(),
        "bl": generate_random_utf8_blob(10),
        "w": generate_random_polygon(),
        "g": generate_random_polygon(),
        "ai": generate_list_of_type(int, 10),
        "v": generate_random_vector(10)
    }


def print_header(header):
    print("=" * (len(header) + 4))
    print(f"= {header} =")
    print("=" * (len(header) + 4))


def print_statement(title, statement):
    print(f"\n\n{title}")
    print("=" * len(title))
    print(str(statement).strip())


def print_data(title, stmt, result):

    print_statement(title, stmt)

    # SQL Statement    
    print("=" * max([len(line) for line in str(stmt).strip().split("\n")]))

    if not result.rowcount:
        print("No data returned.")
        return

    columns = [column for column in result._metadata.keys]
    data = [[str(val) if val is not None else "" for val in row] for row in result]

    column_widths = [max([len(str(row[i])) for row in data] + [len(columns[i])]) for i in range(len(columns))]

    # Column headers
    print(" ".join([f"{columns[i]:{column_widths[i]}}" for i in range(len(columns))]))
    print(" ".join([f"{'-'*column_widths[i]:{column_widths[i]}}" for i in range(len(columns))]))

    # Column values
    for row in data:
        print(" ".join([f"{str(row[i]):{column_widths[i]}}" for i in range(len(row))]))


def check_data(title, metadata, conn, schema, table, sort_column):

    check_query = select("*").select_from(Table(table, metadata, autoload_with = conn, schema = schema)).order_by(column(sort_column))
    check_result = conn.execute(check_query)
    print_data(title, check_query, check_result)


def check_table(conn, schema, table):
    if KineticaDialect().has_table(conn, table, schema):
        return True
    else:
        print(f"\n\nSkipping examples using the [{schema}.{table}] table, as it has not been loaded; use GAdmin to load the data.")
        return False
