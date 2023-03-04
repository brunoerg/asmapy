import ipaddress
import math
import re 

from utils.file import load_file
from utils.asmap import prefix_to_net


def remove_port(ips=[]):
    ips_without_port = []
    for ip in ips:
        # Remove port from ip
        re_for_ip = re.match(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ip)
        if re_for_ip:
            ip = re_for_ip[0]
        if ']' in ip:
            ip = ip.split(']:', 1)[0]
            ip = ip.replace('[', '')
        ips_without_port.append(ip)
    return ips_without_port


def diff(infile1, infile2, ignore_unassigned=False, ips=[]):
    if len(ips) > 0:
        ips = remove_port(ips)
    state1 = load_file(infile1)
    state2 = load_file(infile2)
    ipv4_changed = 0
    ipv6_changed = 0
    old_asn_changed = []
    for prefix, old_asn, new_asn in state1.diff(state2):
        if ignore_unassigned and old_asn == 0:
            continue
        net = prefix_to_net(prefix)
        if isinstance(net, ipaddress.IPv4Network):
            ipv4_changed += 1 << (32 - net.prefixlen)
        elif isinstance(net, ipaddress.IPv6Network):
            ipv6_changed += 1 << (128 - net.prefixlen)
        if new_asn == 0:
            print("# %s was AS%i" % (net, old_asn))
        elif old_asn == 0:
            print("%s AS%i # was unassigned" % (net, new_asn))
        else:
            if len(ips) > 0:
                if old_asn not in old_asn_changed:
                    old_asn_changed.append(old_asn)
                    for ip in ips:
                        ip_type = "IPv4" if type(ipaddress.ip_address(ip)) is ipaddress.IPv4Address else "IPv6"
                        network_type = "IPv4" if type(ipaddress.ip_network(net)) is ipaddress.IPv4Network else "IPv6"
                        if ip_type == "IPv4" and network_type == "IPv4":
                            if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network(net):
                                print(f"{old_asn} -> {new_asn}")
                                break
                        elif ip_type == "IPv6" and network_type == "IPv6":
                            if ipaddress.IPv6Address(ip) in ipaddress.IPv6Network(net):
                                print(f"{old_asn} -> {new_asn}")
                                break

            else:
                print("%s AS%i # was AS%i" % (net, new_asn, old_asn))
    print(
            "# %i%s IPv4 addresses changed; %i%s IPv6 addresses changed"
            % (
                ipv4_changed,
                "" if ipv4_changed == 0 else " (2^%.2f)" % math.log2(ipv4_changed),
                ipv6_changed,
                "" if ipv6_changed == 0 else " (2^%.2f)" % math.log2(ipv6_changed),
            )
        )