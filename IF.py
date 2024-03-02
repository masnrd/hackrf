import numpy as np
from sklearn.ensemble import IsolationForest
from Analyzer import Analyzer
from matplotlib.axes import Axes
from typing import List

class IsolationForest_Analyzer(Analyzer):
    """
    A class that extends the Analyzer abstract class, implementing anomaly detection using Isolation Forest.

    Attributes:
        model (IsolationForest): An Isolation Forest model for detecting anomalies.
        data (List[List[float]]): A list to keep track of data for fitting the model.
    """

    def __init__(self) -> None:
        """
        Initializes the IsolationForest_Analyzer with a predefined Isolation Forest model configuration.
        """
        self.model: IsolationForest = IsolationForest(n_estimators=100, contamination=0.01)
        self.data: List[List[float]] = []

    def plotData(self, average_hz: List[float], db: List[float], ax: Axes) -> None:
        """
        Fits the Isolation Forest model to the data and plots the anomalies identified by the model.

        Args:
            average_hz (List[float]): A list of average frequencies.
            db (List[float]): A list of decibel (dB) values corresponding to the frequencies.
            ax (Axes): The matplotlib Axes object where the data is plotted.
        """
        # Prepare the data for the Isolation Forest model
        self.data = [[hz, db_val] for hz, db_val in zip(average_hz, db)]
        X = np.array(self.data)
        
        # Fit the Isolation Forest model and predict anomalies
        self.model.fit(X)
        anomalies = self.model.predict(X)
        
        # Plot the data points, highlighting anomalies in red
        ax.scatter(X[anomalies == -1, 0], X[anomalies == -1, 1], s=2, color='red', edgecolors='black', label='Anomaly')
        ax.scatter(average_hz, db, s=1, alpha=0.5)
