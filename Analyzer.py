from abc import ABC, abstractmethod
from matplotlib.axes import Axes

class Analyzer(ABC):
    """
    Abstract base class for signal analyzers.
    """

    @abstractmethod
    def plotData(self, average_hz, db, ax: Axes) -> None:
        """
        Plot the data on the given axes.
        
        Args:
            average_hz (np.ndarray): The average frequencies to plot.
            db (np.ndarray): The decibel values to plot.
            ax (plt.Axes): The matplotlib axes to plot on.

        Abstract method to plot frequency and dB values on a matplotlib Axes. 
        Subclasses must implement this method to analyze and visualize the data 
        according to their specific algorithm (e.g., identifying anomalies, clustering). 
        The method takes lists of frequencies and dB values, and a matplotlib Axes object for plotting.
        """
        pass