import csv
import io
import logging
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd


def tuples_to_df(rows: list[tuple], columns: Iterable[str]) -> pd.DataFrame:
    """Converts a list of tuples into a pandas DataFrame."""
    if not rows:
        return pd.DataFrame(columns=list(columns))
    return pd.DataFrame.from_records(rows, columns=list(columns))


def ndarray_to_df(rows: np.ndarray, columns: Iterable[str]) -> pd.DataFrame:
    """Converts a NumPy ndarray into a pandas DataFrame."""
    return pd.DataFrame(data=rows, columns=list(columns))


def dicts_to_df(
    rows: list[dict], columns: Optional[Iterable[str]] = None
) -> pd.DataFrame:
    """Converts a list of dictionaries (row-oriented) into a pandas DataFrame."""
    return pd.DataFrame.from_records(rows, columns=list(columns) if columns else None)


def excel_to_df(path: bytes | str | Path, **kwargs) -> pd.DataFrame:
    """Reads an Excel file into a pandas DataFrame."""
    if isinstance(path, bytes):
        logging.info("Loading Excel from bytes content.")
        return pd.read_excel(path, **kwargs)
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_excel(path, **kwargs)


def csv_to_df(
    path: str | Path, delimiter: Optional[str] = None, **kwargs
) -> pd.DataFrame:
    """Reads data from a CSV file into a pandas DataFrame, auto-detecting the delimiter."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    logging.info(f"Loading CSV file from: {path}")
    if delimiter is None:
        logging.info("Delimiter not specified, attempting to detect.")
        try:
            with open(path, "r", encoding="utf-8") as f:
                delimiter = csv.Sniffer().sniff(f.read(2048)).delimiter
                logging.info(f"Detected delimiter: '{delimiter}'")
        except Exception as e:
            logging.warning(
                f"Could not auto-detect delimiter: {e}. Falling back to default comma ','."
            )
            delimiter = ","

    # Use 'c' engine for performance with single-char delimiters
    engine = "c" if len(delimiter) == 1 else "python"
    kwargs.setdefault("engine", engine)
    return pd.read_csv(path, delimiter=delimiter, **kwargs)
