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
import socket
import pickle

RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'  # Resets the color to default

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
        receiver_ip = "192.168.69.168"
        receiver_port = 12345
        sensor = HackRFModule(analyzer, "192.168.69.168", 12345)
        print("Set up")
        while True:
            try:
            	count, threshold  = sensor.scan(channel=8, time_frame=2, threshold=3)
            	print(f"Detection: {count > threshold}")
            	if count > threshold:
            	    print(f'{GREEN}Phone detected with count {count}{RESET}') 
            	    serialized_data = pickle.dumps(f'Phone detected with count {count}')
            	    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.connect((receiver_ip, receiver_port))
                        header = len(serialized_data).to_bytes(4, byteorder='big') + 0x02.to_bytes(1, byteorder='big')
                        message = header + serialized_data
                        sock.sendall(message)
            	else:
            	    print(f'{RED}Phone not detected with count {count}{RESET}') 
            	    serialized_data = pickle.dumps(f'Phone not detected with count {count}')
            	    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.connect((receiver_ip, receiver_port))
                        header = len(serialized_data).to_bytes(4, byteorder='big') + 0x02.to_bytes(1, byteorder='big')
                        message = header + serialized_data
                        sock.sendall(message)
            except KeyboardInterrupt:
                print("\nShutting down")
                break
            except:
                pass
    else:
        print("Device not found")

if __name__ == "__main__":
    main()
