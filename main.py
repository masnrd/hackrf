import subprocess
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List

def log_line(line, log_file):
    """Log line into log file """
    # with open(log_file, "a") as f:
    #     f.write(line)
    pass

def process_stream(line):
    elements = line.split(", ")
    columns = ["date","time", "hz_low", "hz_high", "width", "sample_count"]
    record_metadata = {}
    for col, e in zip(columns, elements):
        record_metadata[col] = e
    
    out = []
    for i in range(int((float(record_metadata["hz_high"])-float(record_metadata["hz_low"]))/float(record_metadata["width"]))):
        combined_datetime_string = f"{record_metadata['date']} {record_metadata['time']}"
        record = {
            "datetime": datetime.strptime(combined_datetime_string, "%Y-%m-%d %H:%M:%S.%f"),
            "average_hz": float(record_metadata["hz_low"]) + (i+0.5) * float(record_metadata["width"]),
            "db": float(elements[len(columns)+i])
        }
        out.append(record)
    
    return out
        
def print_as_df(entries:List[Dict], log_file):
    print("DATAFRAME")
    print(pd.DataFrame(entries))
    df = pd.DataFrame(entries)
    df.to_csv(log_file)
    print("Exiting with df...")

def main():
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"logs/log_{timestamp}.csv"

        # Command setup
        command = ["hackrf_sweep", "-f", "2400:2490"]
        env = os.environ.copy()
        env["DYLD_LIBRARY_PATH"] = env.get("DYLD_LIBRARY_PATH", "")

        # Starting the subprocess and capturing its output
        entries = []
        with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, text=True, env=env) as proc:
            for line in proc.stdout:
                # Process each line and log it to the file
                print(line)
                entries.extend(process_stream(line))
                # log_line(line)

        # Ensure the subprocess has finished
        proc.communicate()
    except KeyboardInterrupt:
        df = pd.DataFrame(entries)
        df.to_csv(log_filename)
        print_as_df(entries, log_filename)


if __name__ == "__main__":
    main()
