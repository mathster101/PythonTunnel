
A simple python script to create a network tunnel using the linux TUN/TAP api.

Note: This code requires Neo [https://github.com/mathster101/Neo] to be present

## Things to check

 - ensure both hosts are correctly configured as either client or server
 - ensure that the client has the correct server IP in the code
 - run the commands from tunUp.sh individually and ensure client and server have unique IPs on the same subnet and tun0s are both created
## Configure Routing through tun0 link
 - let us assume that you have 2 hosts A and B and want to route all traffic from B through A
 - On A, edit /etc/sysctl.conf and set **net.ipv4.ip_forward = 1**
 - run *sysctl -p* to load new settings 
 - configure NAT on A by running *iptables -t nat -A POSTROUTING -o <IF_NAME> -j MASQUERADE*
 - Define default gateway on B as *ip route add default via <A_TUN_IP_ADDR> dev tun0*
 - all traffic from B will now be rerouted through the python tunnel into A and NATed
