#!/usr/bin/env python3

import os
from bgpdumpy import BGPDump, TableDumpV2

def parse(dir, all_asn=False):
    routes = []
    for entry in os.scandir(dir):
        if entry.is_file():
            with BGPDump(entry.path) as bgp:
                print(f"Processing {entry.name}...")
                for entry in bgp:
                    if not isinstance(entry.body, TableDumpV2):
                        continue

                    prefix = '%s/%d' % (entry.body.prefix, entry.body.prefixLength)
                    if not all_asn:
                        list_ASN = set([
                            route.attr.asPath.split()[-1]
                            for route
                            in entry.body.routeEntries])

                        for item in list(list_ASN):
                            routes.append(f'{prefix} AS{item}\n')
                    else:
                        list_ASN = set([
                            route.attr.asPath
                            for route
                            in entry.body.routeEntries])
                        
                        for item in list(list_ASN):
                            routes.append(f'{prefix}|{item}\n')

    if not os.path.exists(f"paths-{dir}"):
        os.mkdir(f"paths-{dir}")
    with open(f'paths-{dir}/routes.txt', 'w') as w_file:
        w_file.writelines(routes)
