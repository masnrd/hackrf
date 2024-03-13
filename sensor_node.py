import subprocess
import time
from datetime import datetime
import hdbscan
import numpy as np
from numpy.typing import NDArray
from typing import Dict, List, Any


HACKRF_PREFIX = "./hackrf/host/build/hackrf-tools/src/"

class HDBSCAN_Analyzer():
    """
    An analyzer that uses HDBSCAN clustering to analyze signal data.
    """

    def __init__(self) -> None:
        self.model: hdbscan = hdbscan.HDBSCAN(min_cluster_size=18)
        self.start_time = time.time()
        self.count = 0


    def analyse(self, X: NDArray[np.float64]) -> bool:
        self.model.fit(X)
        labels = self.model.labels_
        centroids = HDBSCAN_Analyzer._calculate_centroids(X, labels)
        if centroids.size > 0:
            y_value_threshold = np.percentile(centroids[:, 2], 75)
            high_y_centroids = centroids[centroids[:, 2] > y_value_threshold]

            for label, centroid_x, centroid_y in high_y_centroids:
                points = X[labels == label]
                if HDBSCAN_Analyzer._cluster_criteria(points):
                    return True
        return False

    @staticmethod
    def _calculate_centroids(X: NDArray[np.float64], labels: np.ndarray) -> NDArray[np.float64]:
        centroids = [(label, *points.mean(axis=0)) for label in set(labels) if label != -1
                     for points in [X[labels == label]]]

        return np.array(centroids)


    @staticmethod
    def _cluster_criteria(points: NDArray[np.float64]) -> bool:
        return (max(points[:, 0]) - min(points[:, 0]) > 3 * 1e6 and
                (max(points[:, 1]) + min(points[:, 1])) / 2 > -63)


class HackRFModule():
    def __init__(self, model: HDBSCAN_Analyzer) -> None:
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
        self.command = [HACKRF_PREFIX+"hackrf_sweep", "-f", " ", "-N", "1", "-w", "32768"]
        self.model = model

    def dataProcessing(self, X: NDArray[np.float64], channel: int) -> NDArray[np.float64]:
        if not isinstance(X, np.ndarray):
            raise TypeError(f"Expected X to be an instance of numpy.ndarray, got {type(X)} instead.")
        if X.dtype != np.float64:
            raise TypeError("X array must be of type np.int_")

        low, high = self.CHANNELS[channel].split(":")
        low = int(low) * 1e6
        high = int(high) * 1e6
        mean_db = np.mean(X[:, 1])
        X = X[X[:, 0] < high]
        X = X[X[:, 0] > low]
        X = X[X[:, 1] > mean_db]
        return X

    def scan(self, channel: int, time_frame: float, threshold: int) -> bool:
        self.command[2] = self.CHANNELS[channel]
        count = 0
        start = time.time()
        while (time.time() - start < time_frame):
            output = subprocess.check_output(self.command, stderr=subprocess.DEVNULL).decode('utf-8')
            X = np.array([[int(record['average_hz']), record['db']]
                          for line in output.split('\n')[:-1]
                          for record in process_stream(line)])
            X = self.dataProcessing(X, channel)
            count += int(self.model.analyse(X))
        return count >= threshold


def check_hackrf_device() -> bool:
    try:
        output = subprocess.check_output([HACKRF_PREFIX+'hackrf_info'], stderr=subprocess.STDOUT, text=True)
        return "Found HackRF" in output
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print("hackrf_info command not found. Please ensure HackRF tools are installed and in your PATH.")
        return False


def process_stream(line: str) -> List[Dict[str, Any]]:
    elements = line.split(", ")
    columns = ["date", "time", "hz_low", "hz_high", "width", "sample_count"]
    record_metadata: Dict[str, str] = {col: e for col, e in zip(columns, elements)}

    out: List[Dict[str, Any]] = []
    for i in range(int((float(record_metadata["hz_high"]) - float(record_metadata["hz_low"])) / float(
            record_metadata["width"]))):
        combined_datetime_string = f"{record_metadata['date']} {record_metadata['time']}"
        record = {
            "datetime": datetime.strptime(combined_datetime_string, "%Y-%m-%d %H:%M:%S.%f"),
            "average_hz": float(record_metadata["hz_low"]) + (i + 0.5) * float(record_metadata["width"]),
            "db": float(elements[len(columns) + i])
        }
        out.append(record)

    return out

def main() -> None:
    status = check_hackrf_device()
    if status:
        analyzer = HDBSCAN_Analyzer()
        sensor = HackRFModule(analyzer)
        while True:
            print(sensor.scan(channel=1, time_frame=5, threshold=5))
    else:
        print("Device not found")


if __name__ == "__main__":
    main()