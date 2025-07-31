# coffy/sql/sqldict.py
# author: nsarathy

"""
A dictionary-like object for SQL query results.
"""

from collections.abc import Sequence
from .sql_view import _show_sqldict_in_browser
import csv
import json


class SQLDict(Sequence):
    """
    A dictionary-like object that holds SQL query results.
    """

    def __init__(self, data):
        """
        Initialize with a list of dictionaries or a single dictionary.
        data -- list or dict - The SQL query results.
        """
        self._data = data if isinstance(data, list) else [data]

    def __getitem__(self, index):
        """
        Get item by index or key.
        index -- Index for list-like access or key for dict-like access.
        Returns the item at the specified index or the value for the key.
        """
        return self._data[index]

    def __len__(self):
        """
        Get the number of items.
        Returns the length of the data.
        """
        return len(self._data)

    def __repr__(self):
        """
        String representation of the SQLDict.
        Returns a formatted string of the SQLDict.
        """
        if not self._data:
            return "<empty result>"

        # Get all column names
        columns = list(self._data[0].keys())
        col_widths = {
            col: max(len(col), *(len(str(row[col])) for row in self._data))
            for col in columns
        }

        # Header
        header = " | ".join(f"{col:<{col_widths[col]}}" for col in columns)
        line = "-+-".join("-" * col_widths[col] for col in columns)

        # Rows
        rows = []
        for row in self._data:
            row_str = " | ".join(
                f"{str(row[col]):<{col_widths[col]}}" for col in columns
            )
            rows.append(row_str)

        return f"{header}\n{line}\n" + "\n".join(rows)

    def as_list(self):
        """
        Convert the SQLDict to a list of dictionaries.
        Returns a list of dictionaries representing the SQL results.
        """
        return self._data

    def to_csv(self, path: str):
        """
        Write the SQLDict data to a CSV file.
        path -- The file path to write the CSV data.
        """
        if not self._data:
            raise ValueError("No data to write.")

        with open(path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self._data[0].keys())
            writer.writeheader()
            writer.writerows(self._data)

    def to_json(self, path: str):
        """
        Write the SQLDict data to a JSON file.
        path -- The file path to write the JSON data.
        """
        if not self._data:
            raise ValueError("No data to write.")

        with open(path, mode="w", encoding="utf-8") as file:
            json.dump(self._data, file, indent=4)

    def view(self, title: str = "SQL Query Results"):
        """
        Generate an HTML view of the SQLDict data.
        title -- The title for the HTML page.
        """
        _show_sqldict_in_browser(self, title)
