import os
from typing import Generator
import pyodbc
from pyxlsbwriter import XlsbWriter

# --- CONFIGURATION ---
# CHANGE THE VALUES BELOW TO MATCH YOUR NETEZZA DATABASE
# Make sure you have an ODBC data source (DSN) configured for Netezza on your system.
password = os.environ.get("NZ_DEV_PASSWORD", "password")
DSN = f"DRIVER={{NetezzaSQL}};SERVER=linux.local;PORT=5480;DATABASE=JUST_DATA;UID=admin;PWD={password};"
# Sample query. Change it to one that works on your database.
QUERY1 = "SELECT * FROM JUST_DATA..DIMACCOUNT"
QUERY2 = "SELECT * FROM JUST_DATA..DIMCURRENCY"
OUTPUT_FILENAME = "real_netezza_output.xlsb"


def row_generator(cursor: pyodbc.Cursor) -> Generator[list[any], None, None]:
    """
    Generates rows from a pyodbc cursor, yielding headers first, followed by data rows.

    Args:
        cursor: A pyodbc cursor object containing query results.

    Yields:
        List[Any]: First yields the list of column headers, then each row as a list.

    Raises:
        pyodbc.Error: If there's an error accessing the cursor's data.
    """
    try:
        # Extract column headers from cursor description
        headers = [column[0] for column in cursor.description]
        yield headers

        # Yield each row until the cursor is exhausted
        while row := cursor.fetchone():
            yield list(row)
    except pyodbc.Error as e:
        raise pyodbc.Error(f"Error processing cursor data: {e}")

def main():
    """
    Tests fetching data from a real Netezza database and writing to an XLSB file.
    """
    if os.path.exists(OUTPUT_FILENAME):
        os.remove(OUTPUT_FILENAME)

    try:
        print(f"Connecting to the database using DSN: '{DSN.split(';')[0]}...'")
        with pyodbc.connect(DSN) as conn:
            cursor = conn.cursor()
            print(f"Executing query: '{QUERY1}'")
            cursor.execute(QUERY1)

            # Use XlsbWriter to write the data
            print(f"Writing data to file '{OUTPUT_FILENAME}'...")
            writer = XlsbWriter(OUTPUT_FILENAME)
            writer.add_sheet("Netezza Export")
            writer.write_sheet(row_generator(cursor))

            writer.add_sheet("query 2")
            print(f"Executing query: '{QUERY2}'")
            cursor.execute(QUERY2)
            writer.write_sheet(row_generator(cursor))
            writer.add_sheet("SQL1")
            writer.write_sheet([["code"],[QUERY1]] ,hidden=True)
            writer.add_sheet("SQL2")
            writer.write_sheet([["code"],[QUERY2]] ,hidden=True)
            writer.save()

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database connection or query execution error: {sqlstate}\n{ex}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Check if the XLSB file was created and is not empty
    if os.path.exists(OUTPUT_FILENAME) and os.path.getsize(OUTPUT_FILENAME) > 0:
        print(f"\nTest completed successfully, file '{OUTPUT_FILENAME}' was created and contains data.")
    else:
        print(f"\nTest failed, file '{OUTPUT_FILENAME}' was not created or is empty.")

    if os.path.exists(OUTPUT_FILENAME):
        os.remove(OUTPUT_FILENAME)


if __name__ == '__main__':
    # Checking if pyodbc is installed
    try:
        import pyodbc
        main()
    except ImportError:
        print("pyodbc library is not installed. Installing...")
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyodbc"])
            main()
        except subprocess.CalledProcessError as e:
            print(f"Failed to install pyodbc. Please install it manually: pip install pyodbc")
            sys.exit(1)

