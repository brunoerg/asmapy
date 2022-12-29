# Copyright (c) 2022 Pieter Wuille
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

import ipaddress
import itertools


def merge_path(ret, net, path, cnt):
    assert len(path) > 0
    asn = path[-1]
    if net not in ret:
        ret[net] = {asn: (path, 1)}
        cnt[0] += 1
    else:
        old_paths = ret[net]
        if asn not in old_paths:
            old_paths[asn] = (path, 1)
            cnt[0] += 1
        else:
            old_path, old_count = old_paths[asn]
            common_len = 0
            while common_len < len(old_path) and common_len < len(path):
                if old_path[-common_len - 1] == path[-common_len - 1]:
                    common_len += 1
                else:
                    break
            old_paths[asn] = (old_path[-common_len:], old_count + 1)
    return True

def valid_asn(asn):
    if asn == 0 or asn == 65535 or (asn >= 65552 and asn <= 131072) or asn == 4294967295:
#        print("Skipping reserved AS%i (RFC1930) for network %s" % (asn, net))
        pass
    elif asn == 23456:
#        print("Skipping transition AS%i (RFC6793) for network %s" % (asn, net))
        pass
    elif (asn >= 64496 and asn <= 64511) or (asn >= 65536 and asn <= 65551):
#        print("Skipping documentation AS%i (RFC4893,RFC5398) for network %s" % (asn, net))
        pass
    elif (asn >= 64512 and asn <= 65534) or (asn >= 4200000000 and asn <= 4294967294):
#        print("Skipping private AS%i (RFC5398,RFC6996) for network %s" % (asn, net))
        pass
    else:
        return True
    return False

def accept_net(net):
    if net.is_multicast:
        print("Skipping multicast network %s" % net)
        pass
    elif net.is_private:
#        print("Skipping private network %s" % net)
        pass
    elif net.is_unspecified:
#        print("Skipping unspecified network %s" % net)
        pass
    elif net.is_reserved:
#        print("Skipping reserved network %s" % net)
        pass
    elif net.is_loopback:
        print("Skipping loopback network %s" % net)
    elif net.is_link_local:
        print("Skipping link-local network %s" % net)
    elif not net.is_global:
#        print("Skipping non-global network %s" % net)
        pass
    elif net.prefixlen == 0:
#        print("Skipping entire network %s" % net)
        pass
    elif net.prefixlen > 48 and isinstance(net, ipaddress.IPv6Network):
#        print("Skipping IPv6 range smaller than a /48: %s" % net)
        pass
    elif net.prefixlen > 24 and isinstance(net, ipaddress.IPv4Network):
#        print("Skipping IPv4 range smaller than a /24: %s" % net)
        pass
    else:
        return True
    return False


def bottleneck(path_to_file):
    routes = 0
    valid_routes = 0
    kept_routes = [0]
    ASNS = set()
    RES = {}
    reports = 0
    
    with open(path_to_file) as f:
        lines = f.readlines()
        for line in lines:
            if '|' in line:
                match = line.split('|')
            else:
                match = line.split(' ')
                match[1] = match[1].split('AS')[1]
            if match:
                routes += 1
                try:
                    net = ipaddress.ip_network(match[0], strict=True)
                except ValueError:
                    net = None
                if net is None:
                    raise ValueError("Cannot parse network %s" % match[0])
                if accept_net(net):
                    path_str = match[1]
                    #print(path_str)
                    path_arr = path_str.split(' ')
                    path_arr = [x for x in path_arr if '{' not in x]
                    path_str = ''.join(path_arr)
                    # Convert to list of AS numbers
                    as_path = [int(x) for x in path_str.split(' ') if len(x) > 0]
                    if len(as_path):
                        # Remove duplicates from the list.
                        as_path = [i[0] for i in itertools.groupby(as_path)]
                        if valid_asn(as_path[-1]):
                            ASNS.add(as_path[-1])
                            #print(RES, net, as_path, kept_routes)
                            merge_path(RES, net, as_path, kept_routes)
                            valid_routes += 1
                    else:
                        print("Skipping empty path for %s: %s" % (net, match[1]))
            else:
                print("Ignoring unparseable line: %s" % line.strip())
            if routes >= (reports + 1) * 10000000:
                print("%i routes, %i valid, %i kept; %i ASNs; %i prefixes" % (valid_routes, routes, kept_routes[0], len(ASNS), len(RES)))
                reports = routes // 10000000

        with open("output-bottlenext.txt", "w") as out:
            for net in sorted(RES, key=ipaddress.get_mixed_type_key):
                paths = RES[net]
                first = True
                for path, cnt in sorted(paths.values(), key=lambda f: (-f[1], f[0])):
                    out.write("%s%s AS%i # %i times %s\n" % ("" if first else "# ", net, path[0], cnt, " ".join("AS%i" % x for x in path)))
                    first = False
                out.write("\n")

        with open("output-final.txt", "w") as out:
            for net in sorted(RES, key=ipaddress.get_mixed_type_key):
                paths = RES[net]
                first = True
                for path, cnt in sorted(paths.values(), key=lambda f: (-f[1], f[0])):
                    out.write("%s%s AS%i # %i times %s\n" % ("" if first else "# ", net, path[-1], cnt, " ".join("AS%i" % x for x in path)))
                    first = False
                out.write("\n")