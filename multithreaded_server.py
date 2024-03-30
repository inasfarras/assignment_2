import socket
import threading
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

shared_resource = 0
readers_count = 0
writers_count = 0
writers_waiting = 0

lock = threading.Lock()
reader_cv = threading.Condition(lock)
writer_cv = threading.Condition(lock)

def handle_client(conn, addr):
    global shared_resource
    global readers_count
    global writers_count
    global writers_waiting

    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        msg = conn.recv(SIZE).decode(FORMAT)
        if not msg:
            break
        elif msg.startswith("READ"):
            print(f"[{addr}] Read request received.")
            with reader_cv:
                while writers_count > 0 or writers_waiting > 0:
                    reader_cv.wait()
                readers_count += 1
            perform_busy_operation()
            conn.send(f"READ:{shared_resource}".encode(FORMAT))
            print(f"[{addr}] Read request processed. Shared resource value sent.")
            with reader_cv:
                readers_count -= 1
                if readers_count == 0 and writers_waiting > 0:
                    writer_cv.notify()
        elif msg.startswith("WRITE"):
            print(f"[{addr}] Write request received.")
            with writer_cv:
                writers_waiting += 1
                while readers_count > 0 or writers_count > 0:
                    writer_cv.wait()
                writers_waiting -= 1
                writers_count += 1
            perform_busy_operation()
            data = msg.split(":")[1]
            shared_resource = int(data)
            conn.send("WRITE:OK".encode(FORMAT))
            print(f"[{addr}] Write request processed. Shared resource updated.")
            with writer_cv:
                writers_count -= 1
                if writers_waiting > 0:
                    writer_cv.notify()
                else:
                    reader_cv.notify_all()

    conn.close()

def perform_busy_operation():
    for _ in range(2000000):
        pass

def main():
    print('Server is starting...')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        print(f"Connection with {addr} has been established.")
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == '__main__':
    main()
