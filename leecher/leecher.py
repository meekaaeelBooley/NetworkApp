import socket
import json
import os
import threading

UDP_IP = "10.0.0.03"  # Tracker IP
UDP_PORT = 12000        # Tracker Port
DOWNLOADS_DIR = "downloads"  # Directory to save downloaded files
CHUNK_SIZE = 1024 * 1024  # 1 MB chunks

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
        print(f"Connected to seeder at {seeder_ip}:{seeder_port} for chunk {start}-{end} of file {filename}")

        # Send the filename and chunk range to the seeder
        request = f"{filename},{start},{end}"
        tcp_sock.sendall(request.encode('utf-8'))

        # Receive the chunk and write it to the output file
        with open(output_file, "r+b") as file:
            file.seek(start)
            while start < end:
                chunk = tcp_sock.recv(min(CHUNK_SIZE, end - start))
                if not chunk:
                    break
                file.write(chunk)
                start += len(chunk)
        print(f"Downloaded chunk {start}-{end} of file {filename}.")
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

    # Divide the file into chunks and assign them to seeders
    num_seeders = len(peers)
    chunk_size = file_size // num_seeders
    threads = []

    for i, (seeder_ip, seeder_port) in enumerate(peers):
        start = i * chunk_size
        end = start + chunk_size if i < num_seeders - 1 else file_size
        thread = threading.Thread(target=download_chunk, args=(seeder_ip, seeder_port, filename, start, end, output_file))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

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