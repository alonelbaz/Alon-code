from my_socket import MySocket

HOST = '127.0.0.1'
PORT = 5000

client = MySocket()
client.connect(HOST, PORT)

messages = ["Hello!", "How are you?", "Goodbye!"]

for msg in messages:
    client.send(msg)
    response = client.receive()
    print(f"  --> {response}\n")

client.close()
