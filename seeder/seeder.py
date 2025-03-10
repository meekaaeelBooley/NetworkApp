import socket
import json
import threading
import time
import os
import hashlib

UDP_IP = "10.0.0.20"  # Tracker IP
UDP_PORT = 8500        # Tracker Port
TCP_PORT = 12640       # TCP port for file sharing
FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")    # Directory 

# Register with the tracker
def register_with_tracker(filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = {
        "command": "register",
        "filename": filename,
        "port": TCP_PORT
    }
    json_data = json.dumps(data).encode('utf-8')
    sock.sendto(json_data, (UDP_IP, UDP_PORT))
    message, serverAddress = sock.recvfrom(2048)
    print(message.decode())
    sock.close()

# Send heartbeat to the tracker
def send_heartbeat(filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        time.sleep(60)  # Send heartbeat every 60 seconds
        data = {
            "command": "heartbeat",
            "file_id": filename,
            "port": TCP_PORT
        }
        json_data = json.dumps(data).encode('utf-8')
        sock.sendto(json_data, (UDP_IP, UDP_PORT))
        print(f"Sent heartbeat to tracker for file {filename}")

# Serve specific chunks of a file to leechers
def serve_file_chunks(conn):
    try:
        # Receive the filename and chunk range from the leecher
        request = conn.recv(1024).decode('utf-8')
        filename, start, end = request.split(',')
        start = int(start)
        end = int(end)

        file_path = os.path.join(FILES_DIR, filename)

        # If start and end are 0, send the file size
        if start == 0 and end == 0:
            file_size = os.path.getsize(file_path)
            conn.sendall(str(file_size).encode('utf-8'))
            print(f"Sent file size for {filename}: {file_size} bytes")
            return

        # Serve the requested chunk
        with open(file_path, "rb") as file:
            file.seek(start)  # Move to the start of the chunk
            chunk = file.read(end - start)  # Read the chunk

             # Compute SHA-256 hash of the chunk
            chunk_hash = hashlib.sha256(chunk).hexdigest()
            
            # Send the hash (64 bytes) followed by the chunk
            conn.sendall(chunk_hash.encode('utf-8'))
            conn.sendall(chunk)

        print(f"Sent chunk {start}-{end} of {filename} with hash {chunk_hash}")
    except Exception as e:
        print(f"Error serving file chunk: {e}")
    finally:
        conn.close()

# Start TCP server to listen for leechers
def start_tcp_server():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind(("0.0.0.0", TCP_PORT))
    tcp_sock.listen(5)
    print(f"TCP server started on port {TCP_PORT} for file sharing.")

    while True:
        conn, addr = tcp_sock.accept()
        print(f"Connected to leecher at {addr}")
        threading.Thread(target=serve_file_chunks, args=(conn,)).start()

if __name__ == "__main__":
    # Ensure the files directory exists
    if not os.path.exists(FILES_DIR):
        print(f"Error: The directory '{FILES_DIR}' does not exist.")
        exit(1)

    # List all files in the 'files' directory to share
    files_to_share = [f for f in os.listdir(FILES_DIR) if os.path.isfile(os.path.join(FILES_DIR, f))]
    
    # Register each file with the tracker
    for filename in files_to_share:
        register_with_tracker(filename)
        
        # Start heartbeat thread for each file
        heartbeat_thread = threading.Thread(target=send_heartbeat, args=(filename,))
        heartbeat_thread.daemon = True
        heartbeat_thread.start()

    # Start the TCP server (only one instance)
    tcp_thread = threading.Thread(target=start_tcp_server)
    tcp_thread.daemon = True
    tcp_thread.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)