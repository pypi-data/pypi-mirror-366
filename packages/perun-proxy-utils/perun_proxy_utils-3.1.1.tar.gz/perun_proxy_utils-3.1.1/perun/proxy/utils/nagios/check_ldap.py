#!/usr/bin/env python3

import argparse
import sys
import time

from ldap3 import Server, Connection, SUBTREE

"""
check LDAP is available
"""


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description="Check LDAP status")
    parser.add_argument(
        "-u",
        "--user",
        help="LDAP username",
    )
    parser.add_argument(
        "-p",
        "--password",
        help="LDAP password, required when username is set",
    )
    parser.add_argument(
        "-b",
        "--base",
        help="base dn of LDAP tree",
        required=True,
    )
    parser.add_argument(
        "-i",
        "--identity",
        default="",
        help="eduPersonPrincipalName which the script will look for",
    )
    parser.add_argument(
        "-q",
        "--query",
        help="custom query to test LDAP connection",
    )
    parser.add_argument(
        "-t",
        "--host",
        help="LDAP hostname, 'ldaps://' will be prepended",
        required=True,
    )

    return parser.parse_args()


def call_ldap(username, password, base_dn, query, hostname):
    start_time = time.time()
    ldap_result = None
    ldap_connection = None
    try:
        ldap_server = Server(hostname, use_ssl=True)
        ldap_connection = Connection(ldap_server, user=username, password=password)
        ldap_connection.bind()
        ldap_connection.search(base_dn, query, SUBTREE)
        ldap_result = ldap_connection.entries
    except Exception as e:
        error_message = "Failed to connect to LDAP: " + str(e)
    finally:
        if ldap_connection is not None:
            ldap_connection.unbind()

    end_time = time.time()
    total_time = end_time - start_time

    if ldap_result is not None and len(ldap_result) > 0:
        print(f"0 check_ldap - total_time={total_time:.4f} OK")
        return 0

    if ldap_result is not None:
        error_message = "No result was returned from LDAP"
    print(f"2 check_ldap - total_time={total_time:.4f} {error_message}")
    return 2


def main():
    args = get_args()
    hostname = "ldaps://" + args.host
    query = (
        args.query
        if args.query is not None
        else "eduPersonPrincipalNames=" + args.identity
    )
    query = f"({query})"
    return call_ldap(args.user, args.password, args.base, query, hostname)


if __name__ == "__main__":
    sys.exit(main())
