A Python script to create and manage TUN tunnel devices for secure network communication between server and client.

## Features

- Creates TUN virtual network devices
- Supports both server and client modes
- Configures IP addresses for tunnel interfaces
- Establishes encrypted communication channel
- Optional verbose output for debugging

## Requirements

- Python 3.x
- Linux system with TUN support
- Required Python packages:
  - `pyroute2`
  - Custom `Neo` module for communication

## Installation

```bash
pip install pyroute2
```

Note: The `Neo` module must be available in your Python path.

## Usage

### Basic Syntax

```bash
python maketunnel.py --tun-ip <IP_ADDRESS> --ttype <server|client> [OPTIONS]
```

### Server Mode

```bash
python maketunnel.py --tun-ip 10.0.0.1 --ttype server --verbose
```

### Client Mode

```bash
python maketunnel.py --tun-ip 10.0.0.2 --ttype client --client-ip SERVER_IP --verbose
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--tun-ip` | Yes | IP address for the local TUN device |
| `--ttype` | Yes | Connection type: `server` or `client` |
| `--client-ip` | Conditional | Server IP address (required when `--ttype` is `client`) |
| `--verbose` | No | Enable detailed output messages |

## How It Works

1. Creates a TUN virtual network device
2. Configures the device with the specified IP address
3. In server mode: Listens for incoming client connections
4. In client mode: Connects to the specified server IP
5. Routes network traffic between the TUN device and TCP connection
6. Data is exchanged between endpoints through the tunnel

## Example Network Setup

Server:
```bash
sudo python maketunnel.py --tun-ip 10.0.0.1 --ttype server --verbose
```

Client:
```bash
sudo python maketunnel.py --tun-ip 10.0.0.2 --ttype client --client-ip 192.168.1.100 --verbose
```

After connection, you can test connectivity:
```bash
# On server
ping 10.0.0.2

# On client
ping 10.0.0.1
```

## Notes

- Must be run with sufficient privileges to create TUN devices (typically root)
- The `Neo` module handles the underlying communication protocol
- Default subnet mask is /24 (255.255.255.0)
- Use Ctrl+C to gracefully shut down the tunnel
