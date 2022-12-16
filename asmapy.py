#!/usr/bin/env python3
# Copyright (c) 2022 Pieter Wuille
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

import argparse
import sys
from utils.diff import diff
from utils.parse import parse
from utils.construct import construct
from utils.convert_to_binary import convert_to_binary
from utils.aggregate import aggregate
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
    parser_aggregate = subparsers.add_parser("aggregate", help="Aggregates paths and assigns every IP prefix to the first element of the common suffix of the asn path")
    parser_aggregate.add_argument('path', help="path with files to be aggregated")
    parser_convert.add_argument('-a', '--allasn', dest="all_asn",
                                 help="fetch all ASN for every prefix instead of unique originating ones", default=False, action="store_true")
    parser_binary = subparsers.add_parser("to-binary", help="convert human-readable dump into binary asmap file")
    parser_binary.add_argument('path', help="path to the file to be converted")

    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    elif args.subcommand == "to-human-readable":
        parse(args.path, args.all_asn)
    elif args.subcommand == "aggregate":
        aggregate(args.path)
    elif args.subcommand == "to-binary":
        convert_to_binary(args.path)
    elif args.subcommand == "diff":
        diff(args.infile1, args.infile2, args.ignore_unassigned)
    elif args.subcommand == "download":
        construct(args.date)
    else:
        parser.print_help()
        sys.exit("No command provided.")

if __name__ == '__main__':
    main()
