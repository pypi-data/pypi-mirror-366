import argparse
from typing import List


def parse_dummy_tool_args(argv):
    parser = argparse.ArgumentParser(prog='dummy_tool', description='Dummy tool as an example.')
    parser.add_argument('--what_to_print', type=str, default="Dummy tool.", help='Sentence to print.')
    return parser.parse_args(argv)


def dummy_tool(argv: List[str]):
    args = parse_dummy_tool_args(argv)
    print(args.what_to_print)
    return 0
