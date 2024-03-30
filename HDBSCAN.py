import hdbscan
from numpy.typing import NDArray
from Analyzer import Analyzer
from matplotlib.axes import Axes
from typing import List
import numpy as np
import time

RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'  # Resets the color to default

class HDBSCAN_Analyzer():
    """
    An analyzer that uses HDBSCAN clustering to analyze signal data.
    """

    def __init__(self) -> None:
        self.model: hdbscan = hdbscan.HDBSCAN(min_cluster_size=8)
        self.start_time = time.time()
        self.count = 0

    def plotData(self, X: NDArray[np.float64], ax: Axes) -> None:
        """
        Fits the HDBSCAN model to the data and plots the clusters that meet specific criteria.

        Args:
            X: A NumPy array of signal data, where each row contains frequency and dB values.
            ax: The matplotlib axes to plot on.
        """
        self.model.fit(X)
        labels = self.model.labels_
        centroids = []
        for label in set(labels):
            if label != -1:
                points = X[labels == label]
                centroid = points.mean(axis=0)
                centroids.append((label, centroid))
        centroids = np.array([(label, centroid[0], centroid[1]) for label, centroid in centroids])
        if centroids != []:
            y_value_threshold = np.percentile(centroids[:, 2], 75)  # For example, use the 75th percentile as a threshold
            # Filter centroids
            high_y_centroids = centroids[centroids[:, 2] > y_value_threshold]

            ax.scatter(X[:, 0], X[:, 1], s=1, color='grey', alpha=0.5)

            # Highlight only the selected clusters
            for label in high_y_centroids[:, 0]:
                points = X[labels == label]
                
                if max(points[:, 0]) - min(points[:, 0]) > (3 * 1e6) and (max(points[:, 1]) + min(points[:, 1]))/2 > -63:
                    ax.scatter(points[:, 0], points[:, 1], s=2, alpha=0.75, color='r', label=f'Cluster {int(label)}')
                    self.count += 1
                if time.time() - self.start_time > 5:
                    self.start_time = time.time()
                    if self.count >= 5:
                        print(f'{GREEN}Phone detected with {self.count}{RESET}') 
                    else:
                        print(f'{RED}Phone detected with {self.count}{RESET}') 
                    self.count = 0
                # else:
                #     ax.scatter(points[:, 0], points[:, 1], s=2, alpha=0.75, label=f'Cluster {int(label)}')
                # ax.axvline(min(points[:, 0]), color='r', linestyle='--', label=f'Cluster {int(label)} Low F: {min(points[:, 0]):.2f}')
                # ax.axvline(max(points[:, 0]), color='r', linestyle='--', label=f'Cluster {int(label)} Low F: {min(points[:, 0]):.2f}')
        else:
            ax.scatter(X[:, 0], X[:, 1], s=1, color='grey', alpha=0.5)
    
    def analyse(self, X: NDArray[np.float64]) -> bool:
        """
        Analyzes the signal data using HDBSCAN clustering to determine if certain criteria are met.

        Args:
            X: A NumPy array of signal data, where each row contains frequency and dB values.

        Returns:
            True if the analysis criteria are met, otherwise False.
        """
        self.model.fit(X)
        labels = self.model.labels_
        centroids = self._calculate_centroids(X, labels)
        count = 0
        if centroids.shape[0] > 0:
            y_value_threshold = -60
            high_y_centroids = centroids[centroids[:, 2] > y_value_threshold]
            for label, centroid_x, centroid_y in high_y_centroids:
                # points = X[labels == label]
                # if self._cluster_criteria(points):
                count += 1
        return count
    
    def _calculate_centroids(self, X: NDArray[np.float64], labels: np.ndarray) -> NDArray[np.float64]:
        """
        Calculates the centroids of the clusters formed by HDBSCAN.

        Args:
            X: The data points that have been clustered.
            labels: The labels assigned to each data point by HDBSCAN.

        Returns:
            An NDArray of centroids, each row containing the label, x (frequency), and y (dB) of the centroid.
        """
        centroids = []
        for label in set(labels):
            if label != -1:
                points = X[labels == label]
                centroid = points.mean(axis=0)
                centroids.append((label, centroid))
        centroids = np.array([(label, centroid[0], centroid[1]) for label, centroid in centroids])
        
        return centroids
    
    def _cluster_criteria(self, points: NDArray[np.float64]) -> bool:
        """
        Determines if a cluster meets the specific criteria based on frequency spread and signal strength.

        Args:
            points: A NumPy array of points belonging to a cluster, each row contains frequency (Hz) and dB values.

        Returns:
            bool: True if the cluster meets the criteria, False otherwise.
        """
        return (max(points[:, 0]) - min(points[:, 0]) > 3 * 1e6 and
                (max(points[:, 1]) + min(points[:, 1])) / 2 > -63)

                
