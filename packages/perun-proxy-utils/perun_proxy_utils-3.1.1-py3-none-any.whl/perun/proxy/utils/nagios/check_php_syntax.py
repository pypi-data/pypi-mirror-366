#!/usr/bin/env python3

import subprocess
import sys
import argparse


# nagios return codes
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2


def get_args():
    parser = argparse.ArgumentParser(
        description=(
            "Checks whether PHP files have valid syntax, primarily used for checking"
            " automatically generated files"
        )
    )
    parser.add_argument(
        "-c",
        "--container",
        required=True,
        help="Docker container name to run PHP syntax check inside",
    )
    parser.add_argument(
        "-d",
        "--directory",
        required=True,
        help=(
            "path inside container which will be scanned for PHP files, including"
            " subdirectories"
        ),
    )
    return parser.parse_args()


def main():
    args = get_args()
    dir = args.directory
    container = args.container

    container_paths = (
        subprocess.getoutput(
            f"docker exec {container} find {dir} -type f -name '*.php'"
        )
        .strip()
        .split("\n")
    )
    global_result = ""

    for path in container_paths:
        result = subprocess.getoutput(f"docker exec {container} php -l {path}")
        if "No syntax errors" not in result:
            global_result += f"{result}  |  "

    if not global_result:
        print(f"{OK} check_php_syntax - OK")
        sys.exit(OK)
    else:
        print(f"{CRITICAL} check_php_syntax - {global_result}")
        sys.exit(CRITICAL)


if __name__ == "__main__":
    main()
