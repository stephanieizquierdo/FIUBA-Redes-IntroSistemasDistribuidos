import argparse
from lib.handlers.clientHandler import *
from lib.constants import *

def main():
    parser = argparse.ArgumentParser(description="download a file from server.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', help="Increase output verbosity", action="store_true")
    group.add_argument('-q', '--quiet', help="Decrease output verbosity", action="store_true")
    parser.add_argument('-H', '--host', help="Server IP address", required=True)
    parser.add_argument('-p', '--port', help="Server port", type=int, required=True)
    parser.add_argument('-d', '--dst', help="destination file path", type=str, required=True)
    parser.add_argument('-n', '--name', help="File name", required=True)
    protocol = parser.add_mutually_exclusive_group(required=True)
    protocol.add_argument('-saw', '--stopAndWait', help="use stop and wait protocol", action="store_true")
    protocol.add_argument('-sr', '--selectiveRepeat', help="use selective repeat protocol", action="store_true")

    args = parser.parse_args()  # arg, group = parseArguments()
    run_client(args, DOWNLOAD)


main()
