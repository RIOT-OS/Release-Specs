import pexpect


class GNRC:
    def get_ip_addr(self):
        self.pexpect.sendline("ifconfig")
        self.pexpect.expect("inet6 addr: ([:0-9a-f]+) ")
        ip_addr = self.pexpect.match.group(1)
        return ip_addr

    def get_first_iface(self):
        self.pexpect.sendline("ifconfig")
        self.pexpect.expect("Iface  ([\\d]+)")
        return int(self.pexpect.match.group(1))

    def disable_rdv(self, iface):
        self.pexpect.sendline("ifconfig {} -rtr_adv".format(iface))
        self.pexpect.expect("success")

    def add_ip(self, iface, source):
        self.pexpect.sendline("ifconfig {} add {}".format(iface, source))
        self.pexpect.expect("success")

    def add_nib_route(self, iface, route, ip_addr):
        self.pexpect.sendline(
                "nib route add {} {} {}".format(iface, route, ip_addr))

    def ping(self, count, dest_addr, payload_size, delay):
        self.pexpect.sendline(
                "ping6 {} {} {} {}".format(
                    count, dest_addr, payload_size, delay))
        packet_loss = None
        for i in range(count+1):
            exp = self.pexpect.expect(
                    ["bytes from", "([\\d]+) packets transmitted, ([\\d]+) received \
                     , ([\\d]+)% packet loss", "timeout",
                     pexpect.TIMEOUT], timeout=10)

            if exp == 1:
                packet_loss = int(self.pexpect.match.group(3))
                break
            if exp == 2:
                print("x", end="", flush=True)
            else:
                print(".", end="", flush=True)

        return packet_loss


class PktBuf:
    def extract_unused(self):
        self.pexpect.sendline("pktbuf")
        self.pexpect.expect("unused: ([0-9xa-f]+) ")
        return self.pexpect.match.group(1)
