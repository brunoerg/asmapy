#!/usr/bin/env python3
# Copyright (c) 2022 Pieter Wuille
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

import argparse
import sys
import ipaddress
import math
from utils import asmap, construct
from utils.file import load_file, save_binary, save_text

def main():
    parser = argparse.ArgumentParser(description="Tool for performing various operations on texual and binary asmap files.")
    subparsers = parser.add_subparsers(title="valid subcommands", dest="subcommand")

    parser_encode = subparsers.add_parser("encode", help="convert asmap data to binary format")
    parser_encode.add_argument('-f', '--fill', dest="fill", default=False, action="store_true",
                               help="permit reassigning undefined network ranges arbitrarily to reduce size")
    parser_encode.add_argument('infile', nargs='?', type=argparse.FileType('rb'), default=sys.stdin.buffer,
                               help="input asmap file (text or binary); default is stdin")
    parser_encode.add_argument('outfile', nargs='?', type=argparse.FileType('wb'), default=sys.stdout.buffer,
                               help="output binary asmap file; default is stdout")

    parser_decode = subparsers.add_parser("decode", help="convert asmap data to text format")
    parser_decode.add_argument('-f', '--fill', dest="fill", default=False, action="store_true",
                               help="permit reassigning undefined network ranges arbitrarily to reduce length")
    parser_decode.add_argument('-n', '--nonoverlapping', dest="overlapping", default=True, action="store_false",
                               help="output strictly non-overallping network ranges (increases output size)")
    parser_decode.add_argument('infile', nargs='?', type=argparse.FileType('rb'), default=sys.stdin.buffer,
                               help="input asmap file (text or binary); default is stdin")
    parser_decode.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout,
                               help="output text file; default is stdout")

    parser_diff = subparsers.add_parser("diff", help="compute the difference between two asmap files")
    parser_diff.add_argument('-i', '--ignore-unassigned', dest="ignore_unassigned", default=False, action="store_true",
                             help="ignore unassigned ranges in the first input (useful when second input is filled)")
    parser_diff.add_argument('-u', '--unified', dest="unified", default=False, action="store_true",
                             help="output diff in 'unified' format (with +- lines)")
    parser_diff.add_argument('infile1', type=argparse.FileType('rb'),
                             help="first file to compare (text or binary)")
    parser_diff.add_argument('infile2', type=argparse.FileType('rb'),
                             help="second file to compare (text or binary)")
    subparsers.add_parser("download", help="download dumps")

    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    elif args.subcommand == "encode":
        state = load_file(args.infile)
        save_binary(args.outfile, state, fill=args.fill)
    elif args.subcommand == "decode":
        state = load_file(args.infile)
        save_text(args.outfile, state, fill=args.fill, overlapping=args.overlapping)
    elif args.subcommand == "diff":
        state1 = load_file(args.infile1)
        state2 = load_file(args.infile2)
        ipv4_changed = 0
        ipv6_changed = 0
        for prefix, old_asn, new_asn in state1.diff(state2):
            if args.ignore_unassigned and old_asn == 0:
                continue
            net = asmap.prefix_to_net(prefix)
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
        construct.construct()
    else:
        parser.print_help()
        sys.exit("No command provided.")

if __name__ == '__main__':
    main()
