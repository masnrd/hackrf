import socket
import threading

def handle_client(client_socket, client_ip):
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"Received from {client_ip}: {message.decode()}")
    finally:
        client_socket.close()

def server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        while True:
            client_socket, client_ip = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_ip))
            client_thread.start()

if __name__ == "__main__":
    server()