import subprocess
from typing import Tuple, List, Optional
from Analyzer import Analyzer
from matplotlib.axes import Axes
from utils import process_stream
import threading
import os
import numpy as np

RESET_TIME = 10.0

import socket

def send_detected_packet(server_ip, server_port):
    message = "detected"
    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to the server
            sock.connect((server_ip, server_port))
            # Send the message
            sock.sendall(message.encode('utf-8'))
            #print(f"Message '{message}' sent to {server_ip}:{server_port}")
    except Exception as e:
        print(f"Failed to send message. Error: {e}")

class AnimationPlot:
    """
    A class to handle the plotting of live data streams using matplotlib.

    Attributes:
        ax (Axes): The matplotlib axes object where the data is plotted.
        command (List[str]): The command used to call the hackrf_sweep tool.
        env (Dict[str, str]): Environment variables for the subprocess.
        model (Optional[object]): An optional model instance for advanced plotting.
    """

    def __init__(self, ax: Axes, model: Optional[Analyzer] = None) -> None:
        """
        Initializes the AnimationPlot with the given matplotlib axes and an optional model.

        Args:
            ax (Axes): The matplotlib axes object where the data is plotted.
            model (Optional[Analyzer]): An optional model instance for advanced plotting. 
                                      If provided, it should have a 'plot_data' method.
        """
        self.ax = ax
        # self.command = ["hackrf_sweep", "-f", "2390:2434", "-N", "1", "-w", "30000"]
        self.command = ["hackrf_sweep", "-f", "5750:5850", "-N", "1", "-w", "30000"]
        self.env = os.environ.copy()
        self.env["DYLD_LIBRARY_PATH"] = self.env.get("DYLD_LIBRARY_PATH", "")
        self.model = model

        self.detected = False
        self.reset_timer = threading.Timer(RESET_TIME, self.reset_detected_status)
        self.reset_timer.start()


    def getData(self) -> Tuple[List[int], List[float]]:
        """
        Retrieves data from the hackrf_sweep output and processes it into lists of frequencies and dB values.

        Returns:
            Tuple[List[int], List[float]]: Two lists containing the average frequencies and dB values respectively.
        """
        entries = {}
        output = subprocess.check_output(self.command, stderr=subprocess.DEVNULL).decode('utf-8')
        [entries.update({record["average_hz"]: record["db"]}) for line in output.split('\n')[:-1] for record in process_stream(line)]

        average_hz = [int(record) for record in entries.keys()]
        db = [record for record in entries.values()]
        return average_hz, db

    def reset_detected_status(self) -> None:
        """
        Resets the detected status to False every 10 seconds.
        """
        self.detected = False
        # print("detected status reset.")
        # Restart the timer
        self.reset_timer = threading.Timer(RESET_TIME, self.reset_detected_status)
        self.reset_timer.start()

    def animate(self, i: int) -> None:
        """
        The function to update the plot for each frame of the animation.

        Args:
            i (int): The index of the current frame.
        """
        average_hz, db = self.getData()

        self.ax.clear()  
        self.getPlotFormat()

        # self.ax.axvline(2.390e9, color='b', linestyle='--', label=f'lower band: {2.451e9:.2f}')
        # self.ax.axvline(2.434e9, color='b', linestyle='--', label=f'higher band: {2.473e9:.2f}')
        self.ax.axvline(5.75e9, color='b', linestyle='--', label=f'lower Wi-Fi band: 5.15 GHz')
        self.ax.axvline(5.85e9, color='b', linestyle='--', label=f'upper Wi-Fi band: 5.25 GHz')

        mean_db = np.mean(db)
        X = np.array([[hz, db_val] for hz, db_val in zip(average_hz, db)])
        # X = X[X[:, 0] < 2.434e9]
        # X = X[X[:, 0] > 2.390e9]
        X = X[X[:, 0] < 5.85e9]
        X = X[X[:, 0] > 5.75e9]
        X = X[X[:, 1] > mean_db]

        if np.any(X[:, 1] > -60) and not self.detected:
            print("detected")
            send_detected_packet('172.16.92.200', 65432)
            self.detected = True

        self.ax.axhline(mean_db, color='r', linestyle='--', label=f'Mean dBm: {mean_db:.2f}')
        # exponent = 1.2  
        # X[:, 1] = np.power(X[:, 1] - mean_db, exponent) 
        if self.model and hasattr(self.model, 'plotData'):
            # The model should have a 'plot_data' method for custom plotting.
            self.model.plotData(X, self.ax)
        else:
            # Default scatter plot if no model is provided.
            self.ax.scatter(X[:, 0], X[:, 1], s=1, alpha=0.5)
        
        self.ax.legend()

    def getPlotFormat(self) -> None:
        """
        Sets the format of the plot with labels, title, and grid.
        """
        self.ax.set_ylim([-80, 0]) 
        self.ax.set_title('Scatter Plot of Average Hz vs dB')
        self.ax.set_xlabel('Average Hz')
        self.ax.set_ylabel('dBm')
        self.ax.grid(True)
