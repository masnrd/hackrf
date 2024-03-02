import numpy as np
from sklearn.mixture import GaussianMixture
from Analyzer import Analyzer
from matplotlib.axes import Axes
from typing import List

class GMM_Analyzer(Analyzer):
    """
    Gaussian Mixture Model (GMM) Analyzer for clustering and anomaly detection.

    This class utilizes a Gaussian Mixture Model to fit the data and identify clusters.
    It plots the data points colored by their cluster and marks the cluster centers.

    Attributes:
        model (GaussianMixture): The GMM model with a predefined number of components.
        data (List[List[float]]): A list to store data points for model fitting.
    """

    def __init__(self) -> None:
        """Initializes the GMM_Analyzer with a Gaussian Mixture Model of two components."""
        self.model: GaussianMixture = GaussianMixture(n_components=2, random_state=0)
        self.data: List[List[float]] = []

    def plotData(self, average_hz: List[float], db: List[float], ax: Axes) -> None:
        """
        Fits the GMM model to the data and plots the results on the given matplotlib Axes.

        Each data point is colored based on its cluster assignment. The method also plots
        the cluster centers.

        Args:
            average_hz (List[float]): The list of average frequencies for each data point.
            db (List[float]): The list of dB values corresponding to each frequency.
            ax (Axes): The matplotlib Axes object where the data will be plotted.
        """
        # Prepare the data for GMM
        self.data = [[hz, db_val] for hz, db_val in zip(average_hz, db)]
        X = np.array(self.data)
        
        # Fit the GMM model and predict cluster labels
        self.model.fit(X)
        cluster_labels = self.model.predict(X)
        cluster_centers = self.model.means_

        # Color data points based on their cluster label
        colors = ['blue' if label == 0 else 'green' for label in cluster_labels]
        ax.scatter(X[:, 0], X[:, 1], s=1, alpha=0.5, c=colors, label='Clustered Data')

        # Mark cluster centers
        ax.scatter(cluster_centers[:, 0], cluster_centers[:, 1], s=100, color='red', marker='X', label='Cluster Centers')
        ax.legend()
