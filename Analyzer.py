from abc import ABC, abstractmethod
from matplotlib.axes import Axes
from typing import List
from numpy.typing import NDArray
import numpy as np

class Analyzer(ABC):
    """
    Abstract base class for signal analyzers.
    """

    @abstractmethod
    def plotData(self, X:List[List[float]], ax: Axes) -> None:
        """
        Abstract method to plot frequency and dB values on a matplotlib Axes.

        Args:
            X: A NumPy array of signal data, where each row contains frequency and dB values.
            ax: The matplotlib axes to plot on.

        Subclasses must implement this method to analyze and visualize the data according
        to their specific algorithm (e.g., identifying anomalies, clustering).
        """
        pass
    @abstractmethod
    def analyse(self, X: NDArray[np.float64]) -> bool:
        """
        Analyzes the given signal data and returns a boolean result based on the analysis criteria.

        Args:
            X: A NumPy array of signal data, where each row contains frequency and dB values.

        Returns:
            A boolean indicating the result of the analysis.
        """
        pass