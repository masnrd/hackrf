import hdbscan
from Analyzer import Analyzer
from matplotlib.axes import Axes
from typing import List
import numpy as np

class HDBSCAN_Analyzer(Analyzer):

    def __init__(self) -> None:
        self.model: hdbscan = hdbscan.HDBSCAN(min_cluster_size=40)
        self.data: List[List[float]] = []

    def plotData(self, X:List[List[float]], ax: Axes) -> None:
        self.model.fit(X)
        labels = self.model.labels_
        centroids = []
        for label in set(labels):
            if label != -1:
                points = X[labels == label]
                centroid = points.mean(axis=0)
                centroids.append((label, centroid))
        centroids = np.array([(label, centroid[0], centroid[1]) for label, centroid in centroids])
        y_value_threshold = np.percentile(centroids[:, 2], 75)  # For example, use the 75th percentile as a threshold
        # Filter centroids
        high_y_centroids = centroids[centroids[:, 2] > y_value_threshold]

        ax.scatter(X[:, 0], X[:, 1], s=1, color='grey', alpha=0.5)

        # Highlight only the selected clusters
        for label in high_y_centroids[:, 0]:
            points = X[labels == label]
            ax.scatter(points[:, 0], points[:, 1], s=2, alpha=0.75, label=f'Cluster {int(label)}')
