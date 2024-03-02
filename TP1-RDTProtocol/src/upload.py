import argparse
from lib.constants import *
from lib.handlers.clientHandler import run_client


def main():
    parser = argparse.ArgumentParser(description="upload a file to server.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', help="Increase output verbosity", action="store_true")
    group.add_argument('-q', '--quiet', help="Decrease output verbosity", action="store_true")
    parser.add_argument('-H', '--host', help="Server IP address", required=True)
    parser.add_argument('-p', '--port', help="Server port", type=int, required=True)
    parser.add_argument('-s', '--src', help="Source file path", required=True)
    parser.add_argument('-n', '--name', help="File name", required=True)
    protocol = parser.add_mutually_exclusive_group(required=True)
    protocol.add_argument('-saw', '--stopAndWait', help="use stop and wait protocol", action="store_true")
    protocol.add_argument('-sr', '--selectiveRepeat', help="use selective repeat protocol", action="store_true")

    args = parser.parse_args()
    run_client(args, UPLOAD)


main()
