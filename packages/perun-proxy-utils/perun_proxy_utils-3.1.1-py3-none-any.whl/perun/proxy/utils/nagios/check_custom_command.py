#!/usr/bin/env python3

import argparse
import re
import subprocess
import sys

"""
general script to run non-python checks by a custom-defined command
"""


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description="Custom command to run")
    parser.add_argument(
        "-c",
        "--command",
        required=True,
        help="whole command to be executed",
    )

    return parser.parse_args()


def main():
    args = get_args()
    result = subprocess.run(
        args.command,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(re.sub("[ \t\n]+", " ", result.stdout))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
