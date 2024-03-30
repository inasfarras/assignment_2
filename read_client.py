import socket
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

def main(client_id):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"Reader Client {client_id} connected to {IP}:{PORT}")

    for _ in range(10):  # Looping several times to create contention
        client.send("READ".encode(FORMAT))
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"Reader Client {client_id} received: {msg}")
        time.sleep(1)  # Add a small delay for demonstration

    client.send(DISCONNECT_MESSAGE.encode(FORMAT))

if __name__ == '__main__':
    for i in range(3):  # Create 3 reader clients
        main(i+1)
