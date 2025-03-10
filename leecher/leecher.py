import socket
import json
import os
import threading
import hashlib

UDP_IP = "10.0.0.20"  # Tracker IP
UDP_PORT = 8500        # Tracker Port
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")  # Directory to save downloaded files
CHUNK_SIZE = 512 * 1024  # 1 MB chunks

# Get the list of seeders from the tracker
def get_peers(filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = {"command": "get_peers", "filename": filename}
    json_data = json.dumps(data).encode('utf-8')
    sock.sendto(json_data, (UDP_IP, UDP_PORT))
    message, serverAddress = sock.recvfrom(2048)
    sock.close()
    response = json.loads(message.decode())
    return response.get("peers", [])

# Download a specific chunk from a seeder
def download_chunk(seeder_ip, seeder_port, filename, start, end, output_file):
    try:
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.connect((seeder_ip, seeder_port))
        print(f"Connected to seeder at {seeder_ip}:{seeder_port} for chunk {start}-{end}")

        # Send the request
        request = f"{filename},{start},{end}"
        tcp_sock.sendall(request.encode('utf-8'))

        # Receive the chunk hash (64 bytes)
        hash_received = b''
        while len(hash_received) < 64:
            data = tcp_sock.recv(64 - len(hash_received))
            if not data:
                break
            hash_received += data
        hash_received = hash_received.decode('utf-8').strip()

        # Receive the chunk data
        chunk_data = b''
        remaining_bytes = end - start
        while remaining_bytes > 0:
            data = tcp_sock.recv(min(4096, remaining_bytes))  # Adjust buffer size
            if not data:
                break
            chunk_data += data
            remaining_bytes -= len(data)

        # Verify hash
        computed_hash = hashlib.sha256(chunk_data).hexdigest()
        if computed_hash != hash_received:
            print(f"ERROR: Hash mismatch for chunk {start}-{end}. Expected: {hash_received}, Actual: {computed_hash}")
            return  # Optional: Retry logic here

        # Write to file if hash matches
        with open(output_file, "r+b") as file:
            file.seek(start)
            file.write(chunk_data)
        
        print(f"Downloaded and verified chunk {start}-{end} ({len(chunk_data)} bytes)")
    except Exception as e:
        print(f"Error downloading chunk {start}-{end}: {e}")
    finally:
        tcp_sock.close()

# Download file in parallel from multiple seeders
def download_file_in_parallel(filename, peers, file_size):
    # Ensure the downloads directory exists
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    output_file = os.path.join(DOWNLOADS_DIR, filename)

    # Create an empty file of the required size
    with open(output_file, "wb") as file:
        file.write(b"\0" * file_size)

    # Divide the file into 512 KB chunks
    chunk_size = 512 * 1024  # 512 KB
    num_chunks = (file_size + chunk_size - 1) // chunk_size  # Round up
    threads = []

    print(f"Downloading {filename} of size {file_size} bytes in {num_chunks} chunks of 512 KB each")

    for i in range(num_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, file_size)  # Ensure the last chunk doesn't exceed file size
        seeder_ip, seeder_port = peers[i % len(peers)]  # Distribute chunks among seeders
        print(f"Chunk {i}: {start}-{end} assigned to seeder {seeder_ip}:{seeder_port}")
        thread = threading.Thread(target=download_chunk, args=(seeder_ip, seeder_port, filename, start, end, output_file))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Verify file download
    actual_size = os.path.getsize(output_file)
    print(f"File {filename} downloaded. Expected size: {file_size}, Actual size: {actual_size}")
    
    if actual_size != file_size:
        print("WARNING: Downloaded file size does not match expected file size!")

    print(f"File {filename} downloaded successfully to {output_file}.")

if __name__ == "__main__":
    filename = input("enter file name: ")  # File to download
    peers = get_peers(filename)
    if peers:
        # Get the file size from the first seeder (for simplicity)
        seeder_ip, seeder_port = peers[0]
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.connect((seeder_ip, seeder_port))
        tcp_sock.sendall(f"{filename},0,0".encode('utf-8'))  # Request file size
        file_size = int(tcp_sock.recv(1024).decode('utf-8'))
        tcp_sock.close()

        # Download the file in parallel
        download_file_in_parallel(filename, peers, file_size)
    else:
        print(f"No seeders available for the file {filename}.")