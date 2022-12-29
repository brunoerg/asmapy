import argparse
from datetime import datetime


def valid_date(s):
    try:
        datetime.strptime(s, "%Y%m%d")
        return s
    except ValueError:
        msg = f"Invalid date: {s}"
        raise argparse.ArgumentTypeError(msg)
