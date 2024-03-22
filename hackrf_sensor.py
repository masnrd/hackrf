from abc import ABC, abstractmethod
import os
import subprocess
import numpy as np
from utils import process_stream
from Analyzer import Analyzer
from numpy.typing import NDArray
import time
import socket
import pickle

class SensorModule(ABC):
    @abstractmethod
    def scan(self, channel: int, time_frame: float, threshold: int) -> bool:
        """
        Abstract method to scan for signals within a given time frame and threshold.

        Args:
            channel: The channel number to scan.
            time_frame: The duration for which to scan in seconds
            threshold: The threshold value for deciding the result of the scan.

        Returns:
            A boolean value indicating whether the scan criteria are met.
        """
        pass

class HackRFModule(SensorModule):
    """
    A class for interacting with and analyzing signals from a HackRF device.

    Attributes:
        model (Analyzer): An instance of Analyzer used for signal analysis.
    """
    
    def __init__(self, model: Analyzer, ip: str = "", port: int = 0) -> None:
        """
        Initializes the HackRFModule with a specific Analyzer model.

        Args:
            model: An instance of the Analyzer class for analyzing signals.
        """
        if not isinstance(model, Analyzer):
            raise TypeError(f"Expected model to be an instance of Analyzer, got {type(model)} instead.")
        
        self.receiver_ip = ip
        self.receiver_port = port 
        
        self.CHANNELS = {
            1: '2401:2423',
            2: '2406:2428',
            3: '2411:2433',
            4: '2416:2438',
            5: '2421:2443',
            6: '2426:2448',
            7: '2431:2453',
            8: '2436:2458',
            9: '2441:2463',
            10: '2446:2468',
            11: '2451:2473',
            12: '2456:2478',
            13: '2461:2483',
            14: '2473:2495'
        }
        self.command = ["hackrf_sweep", "-f", " " , "-N", "1", "-w", "131072"]
        self.env = os.environ.copy()
        self.env["DYLD_LIBRARY_PATH"] = self.env.get("DYLD_LIBRARY_PATH", "")
        self.model = model

    def dataProcessing(self, X: NDArray[np.float64], channel: int) -> NDArray[np.float64]:
        """
        Processes the signal data for a specific channel, filtering by frequency and dB.

        Args:
            X: A NumPy array of signal data, where each row is [frequency, dB].
            channel: The channel number whose frequency range is to be processed.

        Returns:
            A NumPy array of the processed signal data.
        """
        if not isinstance(X, np.ndarray):
            raise TypeError(f"Expected X to be an instance of numpy.ndarray, got {type(X)} instead.")
        if X.dtype != np.float64:
            raise TypeError("X array must be of type np.int_")
        
        low, high = self.CHANNELS[channel].split(":")
        low = int(low) * 1e6
        high = int(high) * 1e6
        mean_db = np.mean(X[:, 1])
        X = X[X[:, 0] < high]
        X = X[X[:, 0] > low]
        X = X[X[:, 1] > mean_db]
        return X
    
    def scan(self, channel: int, time_frame: float, threshold: int) -> bool:
        """
        Scans for signals over a specified channel, time frame, and threshold using the HackRF device.

        Args:
            channel: The channel number to scan.
            time_frame: The time frame in seconds over which to perform the scan.
            threshold: The threshold for the number of analyses to consider the scan successful.

        Returns:
            True if the number of successful analyses meets or exceeds the threshold, False otherwise.
        """
        if not isinstance(channel, int):
            raise TypeError(f"Channel must be an integer, got {type(channel)} instead.")
        if not isinstance(time_frame, (int, float)):
            raise TypeError(f"Time frame must be a number, got {type(time_frame)} instead.")
        if not isinstance(threshold, int):
            raise TypeError(f"Threshold must be an integer, got {type(threshold)} instead.")
        
        self.command[2] = self.CHANNELS[channel]
        count = 0
        start = time.time()
        while (time.time()-start < time_frame):
            output = subprocess.check_output(self.command, stderr=subprocess.DEVNULL).decode('utf-8')
            X = np.array([[int(record['average_hz']), record['db']] 
                        for line in output.split('\n')[:-1] 
                        for record in process_stream(line)])
            
            # Information about the receiving device
            if self.receiver_ip:
                serialized_X = pickle.dumps(X)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((self.receiver_ip, self.receiver_port))
                    header = len(serialized_X).to_bytes(4, byteorder='big')
                    message = header + serialized_X
                    sock.sendall(message)

            X = self.dataProcessing(X, channel)
            count += int(self.model.analyse(X))
        return count >= threshold
