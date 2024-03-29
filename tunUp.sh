sudo ip link delete tun0
sudo openvpn --mktun --dev tun0 --user mathew
sudo ip link set tun0 up
sudo ip addr add 10.0.0.2/24 dev tun0