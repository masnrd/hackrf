import matplotlib.pyplot as plt
import time
import matplotlib.animation as animation
from animator import AnimationPlot
# Import the analyzer classes if needed
from OCSVM import OneClassSVM_Analyzer
from IF import IsolationForest_Analyzer
from GMM import GMM_Analyzer
from HDBSCAN import HDBSCAN_Analyzer
from hackrf_sensor import HackRFModule
from utils import check_hackrf_device

def main() -> None:
    """Main function to execute the animation plot.

    Sets up the matplotlib figure, initializes the animation plot with the chosen analyzer
    (if an analyzer is provided), and starts the matplotlib animation loop.
    """
    # fig, ax = plt.subplots()

    # # Initialize the AnimationPlot with the matplotlib axes and optional analyzer.
    # # The analyzer argument is omitted here, indicating the default plotting without any analysis.
    # # If an analyzer is needed, pass the appropriate instance, e.g., GMM_Analyzer().
    # analyzer = HDBSCAN_Analyzer()
    # realTimePlot = AnimationPlot(ax, analyzer)
    # time.sleep(2)
    # ani = animation.FuncAnimation(fig, realTimePlot.animate, frames=100, interval=100)
    # plt.show()
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