# Python XLSB Writer

A Python library for writing large data sets to XLSB files efficiently.

## Installation

```bash
pip install pyxlsbwriter
```

## Usage

### Basic Example

```python
from pyxlsbwriter import XlsbWriter
import datetime
from decimal import Decimal

data = [
    ["Name", "Age", "City", "info"],
    [-123, 2147483647, 2147483648, 2147483999],
    ["x", "y", "z", datetime.datetime.today()],
    ["Alice", 25, "New York", datetime.date.today()],
    ["Bob", 30, "London", Decimal(3.14)],
    ["Charlie", 35, "Paris", datetime.datetime.now()],
    [True, False, None, datetime.datetime.utcnow()]
]

# Initialize writer with a specific compression level
with XlsbWriter("output.xlsb", compressionLevel=6) as writer:
    # Add a visible sheet
    writer.add_sheet("Visible Sheet")
    writer.write_sheet(data)

    # Add a hidden sheet
    writer.add_sheet("Hidden Sheet", hidden=True)
    writer.write_sheet([["This sheet is hidden."]])
```

### XlsxWriter Example

```python
from pyxlsbwriter import XlsxWriter
import datetime
from decimal import Decimal

data = [
    ["Name", "Age", "City", "info"],
    [-123, 2147483647, 2147483648, 2147483999],
    ["x", "y", "z", datetime.datetime.today()],
    ["Alice", 25, "New York", datetime.date.today()],
    ["Bob", 30, "London", Decimal(3.14)],
    ["Charlie", 35, "Paris", datetime.datetime.now()],
    [True, False, None, datetime.datetime.utcnow()]
]

# Initialize writer with a specific compression level
with XlsxWriter("output.xlsx", compressionLevel=6) as writer:
    # Add a visible sheet
    writer.add_sheet("Visible Sheet")
    writer.write_sheet(data)

    # Add a hidden sheet
    writer.add_sheet("Hidden Sheet", hidden=True)
    writer.write_sheet([["This sheet is hidden."]])
```

### Streaming from a Database (ODBC)

This example shows how to stream data directly from a database query into an XLSB file. This is highly memory-efficient as it doesn't load the entire dataset into memory.

First, ensure you have `pyodbc` installed:
```bash
pip install pyodbc
```

Then, you can use a generator function to feed data to `XlsbWriter`.

```python
import os
import pyodbc
from typing import Generator
from pyxlsbwriter import XlsbWriter

# --- Configuration ---
# Make sure you have an ODBC driver and a configured DSN, or use a DSN-less connection string.
DSN = "DRIVER={Your ODBC Driver};SERVER=your_server;DATABASE=your_db;UID=your_user;PWD=your_password"
QUERY = "SELECT * FROM YourTable"
OUTPUT_FILENAME = "db_output.xlsb"

def row_generator(cursor: pyodbc.Cursor) -> Generator[list[any], None, None]:
    """
    Generates rows from a pyodbc cursor, yielding headers first, followed by data rows.
    """
    # Extract column headers from cursor description
    headers = [column[0] for column in cursor.description]
    yield headers

    # Yield each row until the cursor is exhausted
    while row := cursor.fetchone():
        yield list(row)

# --- Main Execution ---
try:
    # Connect to the database
    with pyodbc.connect(DSN) as conn:
        cursor = conn.cursor()
        cursor.execute(QUERY)

        # Use XlsbWriter to write the data stream
        with XlsbWriter(OUTPUT_FILENAME) as writer:
            writer.add_sheet("Database Export")
            writer.write_sheet(row_generator(cursor))
            
            # You can also add hidden sheets with metadata, like the query itself
            writer.add_sheet("SQL Query", hidden=True)
            writer.write_sheet([["SQL"], [QUERY]])


    print(f"Successfully created '{OUTPUT_FILENAME}'")

except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(f"Database connection or query execution error: {sqlstate}\n{ex}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

## Performance

`pyxlsbwriter` is designed for high performance, especially when writing large datasets. The binary `.xlsb` format is significantly more compact and faster to write compared to the standard XML-based `.xlsx` format.

A benchmark was performed with a 50000x50 dataset:

| Library        | Time Taken | File Size |
|----------------|------------|-----------|
| `pyxlsbwriter` (XlsbWriter) | 2.48s | 7.52 MB |
| `pyxlsbwriter` (XlsxWriter) | 5.02s | 6.58 MB |
| [`xlsxwriter`](https://pypi.org/project/xlsxwriter/) | 11.56s | 11.35 MB |

Note: The `xlsxwriter` library offers significantly more features than `pyxlsbwriter`, which is why its performance is lower. `pyxlsbwriter` is optimized for high-performance writing of large datasets with a focus on speed and file size efficiency.

You can run this benchmark yourself using the script located in `examples/performance_test.py`.
