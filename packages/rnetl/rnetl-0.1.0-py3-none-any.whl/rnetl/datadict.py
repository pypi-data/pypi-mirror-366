import pandas as pd
import numpy as np

class DataDict:
    """
    Data dictionary for storing and managing model data.
    """
    def __init__(self):
        self._records = {}
        self._reports = {}

    def record(self, name, value, step):
        """Record a value at a specific step."""
        if name not in self._records:
            self._records[name] = []
        self._records[name].append((step, value))

    def report(self, name, value):
        """Report a final value."""
        self._reports[name] = value

    def get_record(self, name):
        """Get all recorded values for a name."""
        if name in self._records:
            return self._records[name]
        return []

    def get_report(self, name):
        """Get a reported value."""
        if name in self._reports:
            return self._reports[name]
        return None

    def to_dataframe(self):
        """Convert records to a pandas DataFrame."""
        df = pd.DataFrame()
        for name, records in self._records.items():
            steps, values = zip(*records)
            df[name] = pd.Series(values, index=steps)
        return df

    def __repr__(self):
        return f"DataDict with {len(self._records)} records and {len(self._reports)} reports"