import matplotlib.pyplot as plt
import time
import matplotlib.animation as animation
from animator import AnimationPlot
# Import the analyzer classes if needed
from OCSVM import OneClassSVM_Analyzer
# from IF import IsolationForest_Analyzer
# from GMM import GMM_Analyzer

def main() -> None:
    """Main function to execute the animation plot.

    Sets up the matplotlib figure, initializes the animation plot with the chosen analyzer
    (if an analyzer is provided), and starts the matplotlib animation loop.
    """
    fig, ax = plt.subplots()

    # Initialize the AnimationPlot with the matplotlib axes and optional analyzer.
    # The analyzer argument is omitted here, indicating the default plotting without any analysis.
    # If an analyzer is needed, pass the appropriate instance, e.g., GMM_Analyzer().
    realTimePlot = AnimationPlot(ax)
    time.sleep(2)
    ani = animation.FuncAnimation(fig, realTimePlot.animate, frames=100, interval=100)
    plt.show()

if __name__ == "__main__":
    print(type(OneClassSVM_Analyzer()))
    main()