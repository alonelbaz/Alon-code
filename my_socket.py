import socket


class MySocket:
    def __init__(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("[MySocket] Socket created.")
        except socket.error as e:
            print(f"[MySocket] Error creating socket: {e}")
            raise

    def connect(self, host, port):
        try:
            self._sock.connect((host, port))
            print(f"[MySocket] Connected to {host}:{port}")
        except socket.error as e:
            print(f"[MySocket] Error connecting: {e}")
            raise

    def send(self, message):
        try:
            self._sock.sendall(message.encode('utf-8'))
            print(f"[MySocket] Sent: {message}")
        except socket.error as e:
            print(f"[MySocket] Error sending: {e}")
            raise

    def receive(self, buffer_size=1024):
        try:
            data = self._sock.recv(buffer_size)
            message = data.decode('utf-8')
            print(f"[MySocket] Received: {message}")
            return message
        except socket.error as e:
            print(f"[MySocket] Error receiving: {e}")
            raise

    def close(self):
        try:
            self._sock.close()
            print("[MySocket] Connection closed.")
        except socket.error as e:
            print(f"[MySocket] Error closing: {e}")


class MyServerSocket:
    def __init__(self, host, port):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.bind((host, port))
            self._sock.listen(1)
            print(f"[MyServerSocket] Listening on {host}:{port}")
        except socket.error as e:
            print(f"[MyServerSocket] Error starting server: {e}")
            raise
        self._conn = None

    def accept(self):
        try:
            self._conn, addr = self._sock.accept()
            print(f"[MyServerSocket] Client connected from {addr}")
        except socket.error as e:
            print(f"[MyServerSocket] Error accepting connection: {e}")
            raise

    def receive(self, buffer_size=1024):
        try:
            data = self._conn.recv(buffer_size)
            message = data.decode('utf-8')
            print(f"[MyServerSocket] Received: {message}")
            return message
        except socket.error as e:
            print(f"[MyServerSocket] Error receiving: {e}")
            raise

    def send(self, message):
        try:
            self._conn.sendall(message.encode('utf-8'))
            print(f"[MyServerSocket] Sent: {message}")
        except socket.error as e:
            print(f"[MyServerSocket] Error sending: {e}")
            raise

    def close(self):
        try:
            if self._conn:
                self._conn.close()
            self._sock.close()
            print("[MyServerSocket] Server closed.")
        except socket.error as e:
            print(f"[MyServerSocket] Error closing: {e}")
