import subprocess
import threading
import os
import numpy as np
from utils import process_stream  # Assuming this utility is used to process data from hackrf_sweep
import socket

RESET_TIME = 10.0

def send_detected_packet(server_ip, server_port):
    message = "detected"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((server_ip, server_port))
            sock.sendall(message.encode('utf-8'))
    except Exception as e:
        print(f"Failed to send message. Error: {e}")

class Detector:
    def __init__(self):
        self.command = ["hackrf_sweep", "-f", "5750:5850", "-N", "1", "-w", "30000"]
        self.env = os.environ.copy()
        self.env["DYLD_LIBRARY_PATH"] = self.env.get("DYLD_LIBRARY_PATH", "")
        self.detected = False
        self.reset_timer = threading.Timer(RESET_TIME, self.reset_detected_status)
        self.reset_timer.start()

    def getData(self):
        entries = {}
        output = subprocess.check_output(self.command, stderr=subprocess.DEVNULL).decode('utf-8')
        [entries.update({record["average_hz"]: record["db"]}) for line in output.split('\n')[:-1] for record in process_stream(line)]
        average_hz = [int(record) for record in entries.keys()]
        db = [record for record in entries.values()]
        return average_hz, db

    def reset_detected_status(self):
        self.detected = False
        self.reset_timer = threading.Timer(RESET_TIME, self.reset_detected_status)
        self.reset_timer.start()

    def detect(self):
        average_hz, db = self.getData()
        mean_db = np.mean(db)
        X = np.array([[hz, db_val] for hz, db_val in zip(average_hz, db)])
        X = X[(X[:, 0] < 5.85e9) & (X[:, 0] > 5.75e9) & (X[:, 1] > mean_db)]

        if np.any(X[:, 1] > -60) and not self.detected:
            print("detected")
            send_detected_packet('172.16.92.200', 65432)
            self.detected = True
