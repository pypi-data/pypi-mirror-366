#!/usr/bin/env python3

import argparse
import re
import sys
import time
import requests

"""
check RPC API is available
"""


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description="Check RPC status")
    parser.add_argument(
        "-u",
        "--username",
        required=True,
        help="username for IdP",
    )
    parser.add_argument(
        "-p",
        "--password",
        required=True,
        help="password for IdP",
    )
    parser.add_argument(
        "-d",
        "--domain",
        help="RPC domain with authentication method (e.g. 'perun.cesnet.cz/ba')",
        required=True,
    )
    parser.add_argument(
        "-i",
        "--id",
        type=int,
        help="valid userId - This id will be used in getUserById call",
        required=True,
    )

    return parser.parse_args()


def call_api(auth, url, user_id):
    start_time = time.time()
    try:
        response = requests.get(url, timeout=10, auth=auth)
        rpc_result = response.text
    except requests.Timeout:
        rpc_result = "Request timeout"
    end_time = time.time()
    total_time = end_time - start_time
    if re.search(r'"id":' + str(user_id), rpc_result):
        print(f"0 check_rpc_status - total_time={total_time:.4f} OK")
        return 0
    else:
        rpc_result = rpc_result.replace("\n", " ")
        print(f"2 check_rpc_status - total_time={total_time:.4f} {rpc_result}")
        return 2


def main():
    args = get_args()
    auth = (args.username, args.password)
    url = f"https://{args.domain}/rpc/json/usersManager/getUserById?id={args.id}"
    return call_api(auth, url, args.id)


if __name__ == "__main__":
    sys.exit(main())
