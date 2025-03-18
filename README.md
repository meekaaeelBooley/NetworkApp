# P2P Mini BitTorrent
Authors: Meekaaeel Booley, Yaqeen Viljoen, Allen Manthata.

A simplified implementation of a BitTorrent-like peer-to-peer file sharing system in Python. This project demonstrates P2P file transfer with a tracker-based architecture.

## Overview

This system consists of three main components:

1. **Tracker**: Central coordinator that keeps track of which peers have which files
2. **Seeder**: Peer that has a complete file and shares it with others
3. **Leecher**: Peer that downloads files from seeders and can later become a seeder

## Features

- UDP-based tracker for peer discovery and registration
- TCP-based file transfer between peers
- Parallel downloading from multiple seeders
- File integrity verification using SHA-256 hashing
- Automatic peer cleanup for inactive connections
- Seamless transition from leecher to seeder

## Components

### Tracker (`tracker.py`)

The tracker serves as a central coordination point:
- Accepts UDP connections for peer registration and discovery
- Maintains a list of available peers for each file
- Handles periodic ping messages to track active seeders
- Automatically removes inactive peers (5-minute timeout)

### Seeder (`seeder.py`)

Seeders share files with other peers:
- Registers available files with the tracker
- Serves file chunks over TCP connections
- Calculates SHA-256 hashes for chunk verification
- Sends periodic pings to maintain active status

### Leecher (`leecher.py`)

Leechers download files from seeders:
- Gets peer lists from the tracker
- Downloads chunks in parallel from multiple seeders
- Verifies chunk integrity using SHA-256 hashes
- Can transition to become a seeder after downloading

### Main Menu (`main.py`)

Provides a simple CLI (command line interface) for choosing roles:
- Start as a tracker
- Start as a seeder
- Start as a leecher (with option to become a seeder after download)

## Setup and Configuration

1. Configure `config.json` with appropriate IP addresses and ports
2. Create a `downloads` directory in the same folder as the scripts

### Configuration (config.json)

```json
{
    "UDP_IP": "10.0.0.20",       // Tracker IP address
    "UDP_PORT": "8500",          // Tracker UDP port
    "TCP_PORT": "12640"          // TCP port for file sharing
}
```

## Usage

Run the main script to start:

```bash
python main.py
```

### As a Tracker

1. Select option 1 from the main menu
2. The tracker will start listening for UDP connections

### As a Seeder

1. Place files you want to share in the `downloads` directory
2. Select option 2 from the main menu
3. The seeder will register files with the tracker and start serving them

### As a Leecher

1. Select option 3 from the main menu
2. Enter the filename you want to download
3. After downloading, you can choose to become a seeder for this file

## Communication Protocol

### Tracker Protocol (UDP)

- **Register**: `{"command": "register", "filename": "file.txt", "port": 12640}`
- **Get Peers**: `{"command": "get_peers", "filename": "file.txt"}`
- **Ping**: `{"command": "ping", "file_id": "file.txt", "port": 12640}`

### File Transfer Protocol (TCP)

- **Request Format**: `"filename,start_byte,end_byte"`
- **File Size Query**: `"filename,0,0"`
- **Response Format**: `[64-byte hash][chunk data]`

## Performance

- Files are split into 512KB chunks for efficient transfer
- Multiple chunks can be downloaded simultaneously from different seeders
- SHA-256 hash verification ensures file integrity

## Future Improvements

- Encryption for transfers
- Web interface

## Contributors

- Meekaaeel Booley
- Yaqeen Viljoen
- Allen Manthata
