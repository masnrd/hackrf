import subprocess
from typing import Tuple, List, Optional
from Analyzer import Analyzer
from matplotlib.axes import Axes
from utils import process_stream
import os
import numpy as np
import pandas as pd

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
        self.channel = 11
        self.ax = ax
        # self.CHANNELS = {
        #     1: '2390:2434',
        #     2: '2395:2439',
        #     3: '2400:2444',
        #     4: '2405:2449',
        #     5: '2410:2454',
        #     6: '2415:2459',
        #     7: '2420:2464',
        #     8: '2425:2469',
        #     9: '2430:2474',
        #     10: '2435:2479',
        #     11: '2440:2484',
        #     12: '2445:2489',
        #     13: '2450:2494',
        #     14: '2462:2506'
        # }
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

        self.command = ["hackrf_sweep", "-f", self.CHANNELS[self.channel], "-N", "1", "-w", "30000"]
        self.env = os.environ.copy()
        self.env["DYLD_LIBRARY_PATH"] = self.env.get("DYLD_LIBRARY_PATH", "")
        self.model = model
        self.previous_f = None
        self.data_accumulator = []

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
        X = np.array([[hz, db_val] for hz, db_val in zip(average_hz, db)])
        return average_hz, db

    def animate(self, i: int) -> None:
        """
        The function to update the plot for each frame of the animation.

        Args:
            i (int): The index of the current frame.
        """
        try:
            average_hz, db = self.getData()
            if not self.data_accumulator:  # If the accumulator is empty, initialize it
                for freq in average_hz:
                    self.data_accumulator.append({'frequency': freq, 'intensities': []})
            for i, freq in enumerate(average_hz):
                self.data_accumulator[i]['intensities'].append(db[i])

            self.ax.clear()  
            self.getPlotFormat()
            low, high = self.CHANNELS[self.channel].split(":")
            low = int(low) * 1e6
            high = int(high) * 1e6
            mean_db = np.mean(db)
            X = np.array([[hz, db_val] for hz, db_val in zip(average_hz, db)])
            X = X[X[:, 0] < high]
            X = X[X[:, 0] > low]
            X = X[X[:, 1] > mean_db]
            self.ax.axhline(mean_db, color='r', linestyle='--', label=f'Mean dBm: {mean_db:.2f}')
            if self.model and hasattr(self.model, 'plotData'):
                # The model should have a 'plot_data' method for custom plotting.
                self.model.plotData(X, self.ax)
            else:
                # Default scatter plot if no model is provided.
                self.ax.scatter(X[:, 0], X[:, 1], s=1, alpha=0.5)
            
            self.ax.legend()
        except:
            # self.export_to_csv('output.csv')
            print('Close the graph')

    def export_to_csv(self, filename: str):
        """
        Transforms the accumulated data and exports it to a CSV file.
        """
        # Transform data into a format suitable for pandas DataFrame
        df_data = {'Frequency': [d['frequency'] for d in self.data_accumulator]}
        max_length = max(len(d['intensities']) for d in self.data_accumulator)
        for i in range(max_length):
            df_data[f'Time {i+1}'] = [d['intensities'][i] if i < len(d['intensities']) else np.nan for d in self.data_accumulator]
        
        df = pd.DataFrame(df_data)
        df.to_csv(filename, index=False)

    def getPlotFormat(self) -> None:
        """
        Sets the format of the plot with labels, title, and grid.
        """
        self.ax.set_ylim([-80, 0]) 
        self.ax.set_title('Scatter Plot of Average Hz vs dB')
        self.ax.set_xlabel('Average Hz')
        self.ax.set_ylabel('dBm')
        self.ax.grid(True)
        low, high = self.CHANNELS[self.channel].split(":")
        low = int(low) * 1e6
        high = int(high) * 1e6
        self.ax.axvline(low, color='b', linestyle='--', label=f'lower band: {low:.2f}')
        self.ax.axvline(high, color='b', linestyle='--', label=f'higher band: {high:.2f}')
