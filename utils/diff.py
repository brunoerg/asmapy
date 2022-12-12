import ipaddress
import math
from utils.file import load_file
from utils.asmap import prefix_to_net


def diff(infile1, infile2, ignore_unassigned=False):
    state1 = load_file(infile1)
    state2 = load_file(infile2)
    ipv4_changed = 0
    ipv6_changed = 0
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