#!/usr/bin/env python3
# Copyright (c) 2022 Pieter Wuille
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

import argparse
import sys
from src.diff import diff
from src.bgpdump_parse import parse
from src.construct import construct
from src.convert_to_binary import convert_to_binary
from src.bottleneck import bottleneck
from src.utils import valid_date


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
    parser_diff.add_argument('--ips', default="", help="Path to file with ips. It will print the ASNs related to that ips which has changed", dest="ips_path")
    parser_download = subparsers.add_parser("download", help="download dumps")
    parser_download.add_argument('date', help="date to fetch dumps (format: YYYYMMDD)", type=valid_date)
    parser_convert = subparsers.add_parser("to-human-readable", help="convert dump files to human-readable dumps (getting unique originating ASN for this prefix)")
    parser_convert.add_argument('-p', '--paths', nargs='+', default=[], help="paths with files to be converted", dest="paths")
    parser_convert.add_argument('-a', '--allasn', dest="all_asn",
                                 help="fetch all ASN for every prefix instead of unique originating ones", default=False, action="store_true")
    parser_convert.add_argument('-so', '--singleoutput', dest="single_output",
                                 help="combine all dumps into one file", default=False, action="store_true")
    parser_binary = subparsers.add_parser("to-binary", help="convert human-readable dump into binary asmap file")
    parser_binary.add_argument('path', help="path to the file to be converted")
    parser_mapping = subparsers.add_parser("to-mapping", help="convert (sets of) human-readable dumps into a text file with iprange->asn mappings")
    parser_mapping.add_argument('path', help="path to the file to be converted")

    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    elif args.subcommand == "to-human-readable":
        parse(args.paths, args.all_asn, args.single_output)
    elif args.subcommand == "to-mapping":
        bottleneck(args.path)
    elif args.subcommand == "to-binary":
        convert_to_binary(args.path)
    elif args.subcommand == "diff":
        if args.ips_path:
            with open(args.ips_path) as f:
                diff(args.infile1, args.infile2, args.ignore_unassigned, f.read().splitlines())
        else:
            diff(args.infile1, args.infile2, args.ignore_unassigned)
    elif args.subcommand == "download":
        construct(args.date)
    else:
        parser.print_help()
        sys.exit("No command provided.")

if __name__ == '__main__':
    main()
