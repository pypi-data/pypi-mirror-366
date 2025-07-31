# Python XLSB Writer

A Python library for writing large data sets to XLSB files efficiently.

## Installation

```bash
pip install pyxlsbwriter
```

## Usage

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

writer = XlsbWriter("test.xlsb")
writer.add_sheet("Sheet1")
writer.write_sheet(data)
writer.save()
```
