import subprocess
from typing import Tuple, List, Optional
from Analyzer import Analyzer
from matplotlib.axes import Axes
from utils import process_stream
import os
import numpy as np

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
        self.command = ["hackrf_sweep", "-f", "2390:2434", "-N", "1", "-w", "30000"]
        self.env = os.environ.copy()
        self.env["DYLD_LIBRARY_PATH"] = self.env.get("DYLD_LIBRARY_PATH", "")
        self.model = model

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

    def animate(self, i: int) -> None:
        """
        The function to update the plot for each frame of the animation.

        Args:
            i (int): The index of the current frame.
        """
        average_hz, db = self.getData()

        self.ax.clear()  
        self.getPlotFormat()

        self.ax.axvline(2.390e9, color='b', linestyle='--', label=f'lower band: {2.451e9:.2f}')
        self.ax.axvline(2.434e9, color='b', linestyle='--', label=f'higher band: {2.473e9:.2f}')

        mean_db = np.mean(db)
        X = np.array([[hz, db_val] for hz, db_val in zip(average_hz, db)])
        X = X[X[:, 0] < 2.434e9]
        X = X[X[:, 0] > 2.390e9]
        X = X[X[:, 1] > mean_db]
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
