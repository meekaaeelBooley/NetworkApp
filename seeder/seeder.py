import socket
import json

UDP_IP = "127.0.0.1"  # Server IP
UDP_PORT = 5005        # Server Port
TCP_PORT = 12000

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = {
    "command": "register",
    "filename": "example.txt",
    "port": TCP_PORT
}
json_data = json.dumps(data).encode('utf-8')
# Send JSON data to the server
sock.sendto(json_data, (UDP_IP, UDP_PORT))

message, serverAddress = sock.recvfrom(2048)
print(message.decode())

sock.close()