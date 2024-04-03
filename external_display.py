import socket
import pickle
from threading import Thread, Lock
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from HDBSCAN import HDBSCAN_Analyzer

# Switch to a GUI backend compatible with your environment
plt.switch_backend('TkAgg')
fig, ax = plt.subplots()

data_points = np.empty((0, 2), float)  # Initialize an empty array for data points
analyser = HDBSCAN_Analyzer()

def update_plot(frame):
    global ax, analyser
    ax.clear()  # Clear the axes to redraw
    ax.set_ylim([-80, 0])  # Set the y-axis limits
    ax.set_title('Scatter Plot of Average Hz vs dB')
    ax.set_xlabel('Average Hz')
    ax.set_ylabel('dBm')
    ax.grid(True)

    if data_points.size:
        X = data_points
        mean_db = np.mean(X[:, 1])
        # X = X[X[:, 1] > mean_db]
        ax.axhline(mean_db, color='r', linestyle='--', label=f'Mean dBm: {mean_db:.2f}')
        analyser.plotData(X, ax)
        # ax.scatter(data_points[:, 0], data_points[:, 1], s=1, alpha=0.5)  # Plot the data points

def animate():
    global fig
    anim = FuncAnimation(fig, update_plot, interval=100)  # Update the plot every 100 milliseconds
    plt.show()

def receive_all(sock, n):
    """Helper function to receive n bytes or return None if EOF is hit"""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def handle_client_connection(client_socket):
    global data_points

    header = receive_all(client_socket, 5)
    if header is None:
        print("Connection closed by the client.")
        return

    data_length = int.from_bytes(header[:4], byteorder='big')
    data_type = header[4]

    received_data = receive_all(client_socket, data_length)
    if received_data is None:
        print("Data was not fully received.")
        return
    if data_type == 0x01:
        X = pickle.loads(received_data)  # Deserialize the received data

        # Append new data to the global data_points array
        with Lock():  # Use a lock to prevent concurrent access to data_points
            data_points = X
    if data_type == 0x02:
        text = pickle.loads(received_data)
        print(f"Jetson response: {text}")

    client_socket.close()

def start_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, address = server_socket.accept()
        client_thread = Thread(target=handle_client_connection, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    server_thread = Thread(target=start_server, daemon=True)  # Start the server in a background thread
    server_thread.start()
    animate()  # Run the animate function in the main thread to manage the plotting
