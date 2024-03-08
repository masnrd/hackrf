from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
import subprocess

def log_line(line: str, log_file: str) -> None:
    """Appends a given line of text to a log file.

    This function opens the specified log file in append mode and writes the provided
    line of text to it, ensuring that each entry is recorded sequentially.

    Args:
        line: The line of text to be logged.
        log_file: The path to the log file where the line will be appended.
    """
    with open(log_file, "a") as f:
        f.write(f"{line}\n")

def process_stream(line: str) -> List[Dict[str, Any]]:
    """Processes a single line of stream data, extracting and computing necessary information.

    Parses a comma-separated string of data points, converts and calculates the required
    values, and returns a list of dictionaries, each representing a structured record.

    Args:
        line: A comma-separated string containing data points.

    Returns:
        A list of dictionaries, each representing a record with calculated fields.
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
    """Prints a list of dictionary entries as a pandas DataFrame and logs it to a CSV file.

    This function takes a list of dictionaries, converts them into a pandas DataFrame,
    prints the DataFrame, and then saves it to a specified CSV file.

    Args:
        entries: The entries to be printed and logged.
        log_file: The path to the CSV file where the DataFrame will be saved.
    """
    df = pd.DataFrame(entries)
    print("DATAFRAME\n", df, "\nExiting with df...")
    df.to_csv(log_file, index=False)

def check_hackrf_device() -> bool:
    """Checks if a HackRF device is connected to the system.

    This function executes the `hackrf_info` command and parses its output to determine
    if a HackRF device is found. It returns a boolean value indicating the presence of the device.

    Returns:
        True if a HackRF device is found, False otherwise.
    """
    try:
        output = subprocess.check_output(['hackrf_info'], stderr=subprocess.STDOUT, text=True)
        return "Found HackRF" in output
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print("hackrf_info command not found. Please ensure HackRF tools are installed and in your PATH.")
        return False
