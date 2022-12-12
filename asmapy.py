#!/usr/bin/env python3
# Copyright (c) 2022 Pieter Wuille
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

import argparse
import sys
import ipaddress
import math
from utils.asmap import prefix_to_net
from utils.parse import parse
from utils.construct import construct
from utils.convert_to_binary import convert_to_binary
from utils.file import load_file
from utils.valid_date import valid_date


def main():
    parser = argparse.ArgumentParser(description="Tool for performing various operations on texual and binary asmap files.")
    subparsers = parser.add_subparsers(title="valid subcommands", dest="subcommand")

    parser_diff = subparsers.add_parser("diff", help="compute the difference between two asmap files")
    parser_diff.add_argument('-i', '--ignore-unassigned', dest="ignore_unassigned", default=False, action="store_true",
                             help="ignore unassigned ranges in the first input (useful when second input is filled)")
    parser_diff.add_argument('-u', '--unified', dest="unified", default=False, action="store_true",
                             help="output diff in 'unified' format (with +- lines)")
    parser_diff.add_argument('infile1', type=argparse.FileType('rb'),
                             help="first file to compare (text or binary)")
    parser_diff.add_argument('infile2', type=argparse.FileType('rb'),
                             help="second file to compare (text or binary)")
    parser_download = subparsers.add_parser("download", help="download dumps")
    parser_download.add_argument('date', help="date to fetch dumps (format: YYYYMMDD)", type=valid_date)
    parser_convert = subparsers.add_parser("to-human-readable", help="convert dump files to human-readable dumps (getting unique originating ASN for this prefix)")
    parser_convert.add_argument('path', help="path with files to be converted")
    parser_convert = subparsers.add_parser("to-binary", help="convert human-readable dump into binary asmap file")
    parser_convert.add_argument('path', help="path to the file to be converted")

    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    elif args.subcommand == "to-human-readable":
        parse(args.path)
    elif args.subcommand == "to-binary":
        convert_to_binary(args.path)
    elif args.subcommand == "diff":
        state1 = load_file(args.infile1)
        state2 = load_file(args.infile2)
        ipv4_changed = 0
        ipv6_changed = 0
        for prefix, old_asn, new_asn in state1.diff(state2):
            if args.ignore_unassigned and old_asn == 0:
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
        print("# %i (2^%f) IPv4 addresses changed; %i (2^%f) IPv6 addresses changed" % (ipv4_changed, math.log2(ipv4_changed), ipv6_changed, math.log2(ipv6_changed)))
    elif args.subcommand == "download":
        construct(args.date)
    else:
        parser.print_help()
        sys.exit("No command provided.")

if __name__ == '__main__':
    main()
