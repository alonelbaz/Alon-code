from my_socket import MyServerSocket

HOST = '127.0.0.1'
PORT = 5000

server = MyServerSocket(HOST, PORT)
server.accept()

while True:
    message = server.receive()
    if not message:
        break
    server.send(f"Server got: {message}")

server.close()
