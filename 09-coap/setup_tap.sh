# Set up tap networking for tests.

sudo ip tuntap add tap0 mode tap user ${USER}

# Set HW address to similar format to the IP address we want for testing.
sudo ip link set dev tap0 address 0:0:bb:bb:0:1

# Create hardware-based link-local IP address
sudo ip address add fe80::200:bbff:febb:1/64 dev tap0 scope link

# Add unique local address so we don't rely on a link-local address.
sudo ip address add fd00:bbbb::1/64 dev tap0 scope global

sudo ip link set tap0 up

ifconfig

