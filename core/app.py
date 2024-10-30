import sys
from random import random
import time
import argparse
import traceback

from utils.logger import get_logger

log = get_logger()

def run():
    print("Rome 1.0")
    args = load_args()

    try:
        #if args.command == "command":
        #    loader = Loader(args)
        #    loader.load()

        pass

    except Exception as e:
        log.error(f"CLI error {type(e)}: {e}")
        traceback.print_exc()


def load_args():
    argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-c", "--command", help="Command")

    args = parser.parse_args(argv)

    if args.command is None: args.command = 'status'   
    return args
