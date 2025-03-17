import socket
import json
import time
import threading
from datetime import datetime

config = json.loads(open('config.json').read())
UDP_IP = config['UDP_IP']
UDP_PORT = int(config['UDP_PORT'])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

peers = {}
lock = threading.Lock()

def start_server():
    cleanup_thread = threading.Thread(target=remove_old_peers)
    cleanup_thread.daemon = True
    cleanup_thread.start()

    print(f"UDP server started on {UDP_IP}:{UDP_PORT}")

    while True:
        # Receive data from the client
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(data, addr))
        client_thread.start()

def remove_old_peers():
        while True:
            time.sleep(60)  # Check every minute
            current_time = datetime.now()
            
            with lock:
                for file_id in list(peers.keys()):
                    peers[file_id] = [(ip, port, last_active) for ip, port, last_active in peers[file_id] 
                                          if (current_time - last_active).total_seconds() < 300]  # 5 minutes timeout
                    if not peers[file_id]:
                        del peers[file_id]

def handle_client(data, addr):
    try:
        message = json.loads(data.decode('utf-8'))  
        command = message.get('command') # Header field retrieved from the json message
        print(f"Received JSON from {addr}: {message}")

        if command == 'register':
            register_peer(message, addr)

        elif command == 'get_peers':
            send_peer_list(message, addr)

        elif command == 'ping':
            update_peer_status(message, addr)

    except json.JSONDecodeError as e:
        sock.sendto(json.dumps({'status': 'error', 'message': 'Unknown command'}).encode('utf-8'), addr)
        print(f"Error decoding JSON: {e}")


def register_peer(message, addr):
    filename = message.get('filename')
    port = message.get('port')  # TCP port seeder is listening on
    
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
    
    # Send json response to the peer
    response = {
        'status': 'success',
        'message': 'Registered successfully'
    }
    sock.sendto(json.dumps(response).encode('utf-8'), addr)
    print(f"Registered peer {addr[0]}:{port} for {filename}")

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
    file_id = message.get('file_id')
    port = message.get('port')
    
    with lock:
        if file_id in peers:
            for i, (ip, p, _) in enumerate(peers[file_id]):
                if ip == addr[0] and p == port:
                    peers[file_id][i] = (ip, port, datetime.now())
                    break
    
    response = {
        'status': 'success',
        'message': 'ping received'
    }
    sock.sendto(json.dumps(response).encode('utf-8'), addr)


if __name__ == "__main__":
    start_server()