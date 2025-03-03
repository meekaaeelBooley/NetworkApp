# Mini-BitTorrent-like P2P File Sharing System

This is a simplified implementation of a BitTorrent-like peer-to-peer file sharing system consisting of:
1. A tracker that coordinates peer discovery (UDP)
2. A seeder that provides file chunks for download (TCP)
3. A leecher that downloads chunks from seeders and assembles them into a complete file (TCP)

## Requirements
- Python 3.7+
- No external libraries required (using only standard libraries)

## Setup Instructions

### 1. Start the Tracker
The tracker coordinates peer discovery and must be running first.

```bash
python3 tracker.py
```

By default, the tracker runs on 127.0.0.1:8000.

### 2. Start a Seeder
To share a file, run:

```bash
python3 seeder.py /path/to/your/file.txt
```

Optional arguments:
- `--tracker-host`: Tracker's IP address (default: 127.0.0.1)
- `--tracker-port`: Tracker's port (default: 8000)
- `--host`: Seeder's IP address (default: 127.0.0.1)
- `--port`: Seeder's port (default: 0, which assigns a random port)

The seeder will register with the tracker and start serving chunks of the file.

### 3. Start a Leecher
To download a file, you need its file ID (printed by the seeder):

```bash
python3 leecher.py FILE_ID
```

Optional arguments:
- `--download-dir`: Directory to save the downloaded file (default: 'downloads')
- `--tracker-host`: Tracker's IP address (default: 127.0.0.1)
- `--tracker-port`: Tracker's port (default: 8000)
- `--max-parallel`: Maximum number of parallel downloads (default: 3)

The leecher will:
1. Get a list of seeders from the tracker
2. Download chunks in parallel from multiple seeders
3. Assemble the file once all chunks are downloaded
4. Automatically become a seeder for the file

## Features
- UDP-based tracker for peer discovery
- TCP-based reliable file transfer
- Chunked downloads (512 KB chunks by default)
- Parallel downloads from multiple seeders
- Simple file integrity using file ID
- Automatic re-seeding after download completes
- Tracker cleanup of inactive peers

## Protocol Specification
See the report document for detailed protocol specification and sequence diagrams.