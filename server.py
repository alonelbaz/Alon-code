import socket

HOST = '127.0.0.1'
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on {HOST}:{PORT}")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

while True:
    data = conn.recv(1024)
    if not data:
        break
    message = data.decode('utf-8')
    print(f"Received: {message}")
    response = f"Server got: {message}"
    conn.sendall(response.encode('utf-8'))

conn.close()
server_socket.close()
print("Server closed.")
