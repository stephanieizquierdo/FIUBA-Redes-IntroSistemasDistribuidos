import argparse
from lib.handlers.serverHandler import run_server


def main():
    parser = argparse.ArgumentParser(description="start server.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', help="Increase output verbosity", action="store_true")
    group.add_argument('-q', '--quiet', help="Decrease output verbosity", action="store_true")
    parser.add_argument('-H', '--host', help="service IP address", required=True)
    parser.add_argument('-p', '--port', help="service port", type=int, required=True)
    parser.add_argument('-s', '--storage', help="Storage dir path", required=True)
    protocol = parser.add_mutually_exclusive_group(required=True)
    protocol.add_argument('-saw', '--stopAndWait', help="use stop and wait protocol", action="store_true")
    protocol.add_argument('-sr', '--selectiveRepeat', help="use selective repeat protocol", action="store_true")

    args = parser.parse_args()
    try:
        run_server(args)
    except KeyboardInterrupt:
        print(" pressed. Exiting gracefully.")


main()
