import socket
import json
import threading
from datetime import datetime

UDP_IP = "0.0.0.0" 
UDP_PORT = 5005    

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

peers = {}
lock = threading.Lock()

def start_server():
    print(f"UDP server started on {UDP_IP}:{UDP_PORT}")
    while True:
        # Receive data from the client
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(data, addr))
        client_thread.start()

def handle_client(data, addr):
    try:
        message = json.loads(data.decode('utf-8'))  # Fixed typo here
        command = message.get('command')
        print(f"Received JSON from {addr}: {message}")

        if command == 'register':
            register_peer(message, addr)

        elif command == 'get_peers':
            send_peer_list(message, addr)

        elif command == 'heartbeat':
            update_peer_status(message, addr)

    except json.JSONDecodeError as e:
        sock.sendto(json.dumps({'status': 'error', 'message': 'Unknown command'}).encode('utf-8'), addr)
        print(f"Error decoding JSON: {e}")


def register_peer(message, addr):
    filename = message.get('filename')
    port = message.get('port')  # TCP port the seeder is listening on
    
    with lock:
        if filename not in peers:
            peers[filename] = []
            
        # Check if peer already exists and update it
        peer_exists = False
        for i, (ip, p, _) in enumerate(peers[filename]):
            if ip == addr[0] and p == port:
                peers[filename][i] = (ip, port, datetime.now())
                peer_exists = True
                break
                
        if not peer_exists:
            peers[filename].append((addr[0], port, datetime.now()))
                
    response = {
        'status': 'success',
        'message': 'Registered successfully'
    }
    sock.sendto(json.dumps(response).encode('utf-8'), addr)
    print(f"Registered peer {addr[0]}:{port} for file {filename}")

def send_peer_list(message, addr):
    filename = message.get('filename')
        
    with lock:
        peer_list = []
        if filename in peers:
            for ip, port, _ in peers[filename]:
                peer_list.append((ip, port))
    
    response = {
        'status': 'success',
        'peers': peer_list
    }
    sock.sendto(json.dumps(response).encode('utf-8'), addr)
    print(f"Sent peer list for file {filename} to {addr}")

def update_peer_status(message, addr):
    return None

if __name__ == "__main__":
    start_server()