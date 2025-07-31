#!/usr/bin/env python3
import argparse
import sys

import requests


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description="Check webserver")
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        help="webserver url",
    )
    parser.add_argument("-p", "--port", help="webserver port")

    return parser.parse_args()


def main():
    args = get_args()
    url = args.url

    if args.port:
        url += f":{args.port}"

    status = 2
    status_txt = "ERROR"

    try:
        res = requests.get(url, allow_redirects=False)
        if res.status_code == 200 or res.status_code == 301:
            status = 0
            status_txt = "OK"
    except requests.RequestException:
        pass

    print(str(status) + " webserver_availability - " + status_txt)
    return status


if __name__ == "__main__":
    sys.exit(main())
