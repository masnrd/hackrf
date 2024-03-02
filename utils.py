from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

def log_line(line: str, log_file: str) -> None:
    """
    Appends a given line of text to a log file.

    Args:
        line (str): The line of text to be logged.
        log_file (str): The path to the log file where the line will be appended.
    """
    with open(log_file, "a") as f:
        f.write(line)

def process_stream(line: str) -> List[Dict[str, Any]]:
    """
    Processes a single line of stream data, extracting and computing necessary information.

    Args:
        line (str): A comma-separated string containing data points.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a record with calculated fields.
    """
    elements = line.split(", ")
    columns = ["date", "time", "hz_low", "hz_high", "width", "sample_count"]
    record_metadata: Dict[str, str] = {col: e for col, e in zip(columns, elements)}
    
    out: List[Dict[str, Any]] = []
    for i in range(int((float(record_metadata["hz_high"]) - float(record_metadata["hz_low"])) / float(record_metadata["width"]))):
        combined_datetime_string = f"{record_metadata['date']} {record_metadata['time']}"
        record = {
            "datetime": datetime.strptime(combined_datetime_string, "%Y-%m-%d %H:%M:%S.%f"),
            "average_hz": float(record_metadata["hz_low"]) + (i + 0.5) * float(record_metadata["width"]),
            "db": float(elements[len(columns) + i])
        }
        out.append(record)
    
    return out

def print_as_df(entries: List[Dict[str, Any]], log_file: str) -> None:
    """
    Prints a list of dictionary entries as a pandas DataFrame and logs it to a CSV file.

    Args:
        entries (List[Dict[str, Any]]): The entries to be printed and logged.
        log_file (str): The path to the CSV file where the DataFrame will be saved.
    """
    print("DATAFRAME")
    df = pd.DataFrame(entries)
    print(df)
    df.to_csv(log_file)
    print("Exiting with df...")
