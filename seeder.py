# Authors: Meekaaeel Booley, Yaqeen Viljoen, Allen Manthata
# UCT Computer Science CSC3002F 2025
# Network Assignment

import socket
import json
import threading
import time
import os
import hashlib

config = json.loads(open('config.json').read())
UDP_IP = config['UDP_IP']     # Tracker IP
UDP_PORT = int(config['UDP_PORT']) # Tracker Port

TCP_PORT = int(config['TCP_PORT'])   # TCP port for file sharing
FILES_DIR = os.path.join(os.getcwd(), 'downloads') # downlaods directory 

# register with the tracker
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

# send ping to the tracker
def send_ping(filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        time.sleep(120)  # Send ping every 120 seconds
        data = {
            "command": "ping",
            "file_id": filename,
            "port": TCP_PORT
        }
        json_data = json.dumps(data).encode('utf-8')
        sock.sendto(json_data, (UDP_IP, UDP_PORT))
        print(f"Sent ping to tracker for file {filename}")

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

             # compute SHA-256 hash of the chunk
            chunk_hash = hashlib.sha256(chunk).hexdigest()
            
            # send the hash (64 bytes) followed by the chunk
            conn.sendall(chunk_hash.encode('utf-8'))
            conn.sendall(chunk)

        print(f"Sent chunk {start}-{end} of {filename} with hash {chunk_hash}")
    except Exception as e:
        print(f"Error serving file chunk: {e}")
    finally:
        conn.close()

# start TCP server to listen for leechers
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
    if not os.path.exists(FILES_DIR):
        print(f"Error: The directory '{FILES_DIR}' does not exist.")
        exit(1)

    # List all downloads in the 'downloads' directory to share
    files_to_share = []
    # Get a list of all entries (files)
    all_entries = os.listdir(FILES_DIR)

    # Loop through each entry in the directory
    for entry in all_entries:
        # create the full path to the entry by joining the directory path and the entry name
        full_path = os.path.join(FILES_DIR, entry)
        # check if the entry is a file (not a folder)
        if os.path.isfile(full_path):
            # If it's a file, add it to the list of files to share
            files_to_share.append(entry)


    
    # register each file with the tracker
    for filename in files_to_share:
        register_with_tracker(filename)
        
        # Start ping thread for each file
        ping_thread = threading.Thread(target=send_ping, args=(filename,))
        ping_thread.daemon = True
        ping_thread.start()

    # Start the TCP server (only one instance)
    tcp_thread = threading.Thread(target=start_tcp_server)
    tcp_thread.daemon = True
    tcp_thread.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)