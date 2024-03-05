import numpy as np
from sklearn.svm import OneClassSVM
from Analyzer import Analyzer
from matplotlib.axes import Axes
from typing import List

class OneClassSVM_Analyzer(Analyzer):
    """
    Anomaly detection using One-Class Support Vector Machine (SVM).

    This class utilizes One-Class SVM to identify outliers in the dataset. It is particularly
    useful for novelty detection where the majority of the data is considered 'normal', and
    anomalies or outliers are identified as deviations from this norm.

    Attributes:
        model (OneClassSVM): The One-Class SVM model configured for anomaly detection.
        data (List[List[float]]): A list to store data points for model fitting.
    """

    def __init__(self) -> None:
        """
        Initializes the OneClassSVM_Analyzer with a One-Class SVM model using specified parameters.
        """
        self.model: OneClassSVM = OneClassSVM(nu=0.01, kernel='rbf', gamma='auto')
        self.data: List[List[float]] = []

    def plotData(self, X:List[List[float]], ax: Axes) -> None:
        """
        Fits the One-Class SVM model to the data and plots the results on the given matplotlib Axes.

        Data points are colored based on their classification by the model: blue for inliers and red for outliers.

        Args:
            average_hz (List[float]): The list of average frequencies for each data point.
            db (List[float]): The list of dB values corresponding to each frequency.
            ax (Axes): The matplotlib Axes object where the data will be plotted.
        """
        # Fit the One-Class SVM model and predict
        self.model.fit(X)
        pred = self.model.predict(X)
        
        # Color data points based on the prediction
        colors = np.array(['blue' if p == 1 else 'red' for p in pred])
        ax.scatter(X[:, 0], X[:, 1], s=1, alpha=0.5, c=colors, label='Data Points')
        ax.legend()
