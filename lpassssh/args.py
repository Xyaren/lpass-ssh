import argparse
from argparse import Namespace
from typing import Tuple


def parse_args() -> Tuple[Namespace, argparse.ArgumentParser]:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='lpass-ssh')
    subparsers = parser.add_subparsers(required=False, dest='subparser_name')

    list_parser = subparsers.add_parser("list", help="List available SSH Secrets from LastPass")
    list_parser.add_argument("--table", help="Display as table", action='store_true')
    subparsers.add_parser("load", help="Load available SSH Secrets into the ssh agent.")
    parser.set_defaults(subparser_name="load")
    return parser.parse_args(), parser
