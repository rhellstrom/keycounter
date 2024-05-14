import argparse
from typing import List

def parse_key_list(key_list_str: str) -> List[int]:
    try:
        key_list = [int(key) for key in key_list_str.split(',')]
        return key_list
    except ValueError:
        raise argparse.ArgumentTypeError("Keys must be comma-separated integers")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--event-file", help="Keyboard event file. e.g /dev/input/event13", default=None)
    parser.add_argument("-o", "--output-file", help="Set output filename to something other than session datetime", default=None)
    parser.add_argument("-i", "--write-interval", type=int, help="File update interval in seconds for writing current count to file", default=60)
    parser.add_argument("-k", "--keys", type=parse_key_list, help="Comma-separated list of keys to count", required=True)
    args = parser.parse_args()
    return args

