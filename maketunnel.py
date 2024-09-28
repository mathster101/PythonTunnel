import struct
from fcntl import ioctl
import select
import Neo

#########################################
ttype = "client"# i change this to client on host B
CLIENT_IP = "192.168.0.47"# only for client side
#########################################

def openTun(tunName):
    #huge thanks to https://jvns.ca/blog/2022/09/06/send-network-packets-python-tun-tap/
    tun = open("/dev/net/tun", "r+b", buffering=0)
    LINUX_IFF_TUN = 0x0001
    LINUX_IFF_NO_PI = 0x1000
    LINUX_TUNSETIFF = 0x400454CA
    flags = LINUX_IFF_TUN | LINUX_IFF_NO_PI
    ifs = struct.pack("16sH22s", tunName, flags, b"")
    ioctl(tun, LINUX_TUNSETIFF, ifs)
    return tun

def serverUp():
    comm = Neo.Neo()
    comm.start_server()
    comm.get_new_conn()
    return comm

def clientUp():
    comm = Neo.Neo()
    comm.connect_client(IP=CLIENT_IP)
    return comm
#####################################################

tun = openTun(b"tun0")
if ttype == "server":
    tcp = serverUp()
else:
    tcp = clientUp()
print("sockets are up")

while True:
    inputs = [tun, tcp.sock, tcp.conn]
    outputs = []
    inputs,outputs,errs = select.select(inputs, outputs, inputs)
    for fd in inputs:
        if fd == tun:
            data = tun.read(2000)
            print(len(data), "from tun")
            tcp.send_data(data)
            print("sent")
        if fd == tcp.sock:
            #if client
            data = tcp.receive_data()
            print(len(data), "from tcp")
            tun.write(data)
        if fd == tcp.conn:
            #if server
            data = tcp.receive_data()
            print(len(data), "from tcp")
            tun.write(data)
