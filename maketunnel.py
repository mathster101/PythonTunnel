import struct
import fcntl
import os
import select
import Neo
import argparse
from pyroute2 import IPRoute

#Constants for TUN creation

TUNSETIFF   = 0x400454ca
TUNSETOWNER = 0x400454cc
IFF_TUN     = 0x0001
IFF_NO_PI   = 0x1000

ip = IPRoute()

def createTunDevice(name = 'tun0', owner_uid = None):
	# Open the TUN device
	tun_fd = os.open('/dev/net/tun', os.O_RDWR)
	
	# Create the interface
	ifr = struct.pack('16sH', name.encode(), IFF_TUN | IFF_NO_PI)
	fcntl.ioctl(tun_fd, TUNSETIFF, ifr)
	
	# Set owner if not specified
	if owner_uid is not None:
		fcntl.ioctl(tun_fd, TUNSETOWNER, owner_uid)
	
	return tun_fd

def deleteTunIfExists():
    try:
        idx = ip.link_lookup(ifname = 'tun0')[0]
        ip.link("del", index=idx)
    except IndexError:
        pass # Interface does not exist   

def configureTunDevice(tun_ip, verbose=False):
    # Configure the interface
    idx = ip.link_lookup(ifname = 'tun0')[0]
    ip.link('set', index = idx, state = 'up')
    ip.addr('add', index = idx, address = tun_ip, prefixlen = 24)
    if verbose:
        print("TUN device created and configured successfully")

def serverUp(verbose=False):
    comm = Neo.Neo()
    if verbose:
        print("waiting for connection from client")
    comm.start_server()
    comm.get_new_conn()
    return comm

def clientUp(client_ip, verbose=False):
    comm = Neo.Neo()
    comm.connect_client(IP=client_ip)
    return comm

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create TUN tunnel')
    parser.add_argument('--tun-ip', required=True, help='IP address for the TUN device')
    parser.add_argument('--ttype', choices=['server', 'client'], required=True, help='Type of connection: server or client')
    parser.add_argument('--client-ip', help='Client IP address (required if ttype is client)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate client IP requirement
    if args.ttype == 'client' and not args.client_ip:
        parser.error("--client-ip is required when ttype is client")
    
    # Create TUN Device
    tun_fd = createTunDevice('tun0', owner_uid = None)
    configureTunDevice(args.tun_ip, args.verbose)  # Use the provided IP address

    tcp = None
    fileDescriptorsToMonitor = [tun_fd]

    if args.ttype == "server":
        tcp = serverUp(args.verbose)
        fileDescriptorsToMonitor += [tcp.conn]
    else:
        tcp = clientUp(args.client_ip, args.verbose)
        fileDescriptorsToMonitor += [tcp.sock]
        
    if args.verbose:
        print("sockets are up")

    try:
        while True:
            outputs = []
            inputs,outputs,errs = select.select(fileDescriptorsToMonitor, outputs, fileDescriptorsToMonitor)
            for fd in inputs:
                if fd == tun_fd:
                    data = os.read(tun_fd, 1500)
                    if args.verbose:
                        print(len(data), "from tun")
                    tcp.send_data(data)
                    if args.verbose:
                        print("sent")
                if fd == tcp.sock:
                    #if client
                    data = tcp.receive_data()
                    if args.verbose:
                        print(len(data), "from tcp")
                    os.write(tun_fd, data)
                if fd == tcp.conn:
                    #if server
                    data = tcp.receive_data()
                    if args.verbose:
                        print(len(data), "from tcp")
                    os.write(tun_fd, data)
    except KeyboardInterrupt:
        if args.verbose:
            print("\nKeyboard interrupt received, shutting down...")
    finally:
        os.close(tun_fd)
        if args.verbose:
            print("TUN device closed")

if __name__ == "__main__":
    main()
