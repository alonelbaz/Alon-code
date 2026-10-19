import socket

HOST = '127.0.0.1'
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(f"Connected to server {HOST}:{PORT}")

messages = ["Hello!", "How are you?", "Goodbye!"]

for msg in messages:
    client_socket.sendall(msg.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    print(f"Sent: {msg}")
    print(f"Response: {response}")
    print()

client_socket.close()
print("Connection closed.")
