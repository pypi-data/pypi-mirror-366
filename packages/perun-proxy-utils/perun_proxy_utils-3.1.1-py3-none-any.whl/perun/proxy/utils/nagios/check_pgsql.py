#!/usr/bin/env python3

import argparse
import re
import sys
import time

import psycopg2

# nagios return codes
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


def get_args():
    parser = argparse.ArgumentParser(description="PostgreSQL connection check")
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        help="Host name or IP Address (default: 127.0.0.1)",
        default="127.0.0.1",
    )
    parser.add_argument(
        "-P",
        "--port",
        type=str,
        help="Port number (default: 5432)",
        default="5432",
    )
    parser.add_argument(
        "-c",
        "--critical",
        type=int,
        help="Response time to result in critical status (default: 8s)",
        default=8,
    )
    parser.add_argument(
        "-w",
        "--warning",
        type=int,
        help="Response time to result in warning status (default: 2s)",
        default=2,
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        help="Seconds before connection times out (default: 10s)",
        default=10,
    )
    parser.add_argument(
        "-d",
        "--database",
        type=str,
        help="Database to check (default: template1)",
        default="template1",
    )
    parser.add_argument(
        "-l",
        "--logname",
        type=str,
        help="Login name of user",
    )
    parser.add_argument(
        "-p",
        "--password",
        type=str,
        help="Password (BIG SECURITY ISSUE)",
    )
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        help="SQL query to run. Only first column in first row will be read",
    )
    parser.add_argument(
        "-o",
        "--option",
        type=str,
        help="Connection parameters (keyword = value)",
    )
    parser.add_argument(
        "-W",
        "--query-warning",
        type=threshold_type,
        dest="query_warning",
        help="SQL query value to result in warning status (float). "
        "Single value or range, e.g. '20:50.",
    )
    parser.add_argument(
        "-C",
        "--query-critical",
        type=threshold_type,
        dest="query_critical",
        help="SQL query value to result in critical status (float). "
        "Single value or range, e.g. '20:50",
    )

    return parser.parse_args()


def threshold_type(arg_value):
    threshold_regex = re.compile(r"^\d+(\.\d+)?(:\d+(\.\d+)?)?$")
    if not threshold_regex.match(arg_value):
        raise argparse.ArgumentTypeError("Invalid threshold format.")
    return arg_value


def val_in_threshold(threshold_str, value):
    splitted = threshold_str.split(":")
    if len(splitted) == 1:
        return 0 < value < float(splitted[0])
    else:
        return float(splitted[0]) < value < float(splitted[1])


def do_query(connection, args):
    try:
        with connection.cursor() as cursor:
            cursor.execute(args.query)
            if len(cursor.description) < 1:
                print("QUERY WARNING - No columns returned.")
                return WARNING
            rows = cursor.fetchone()
            if len(rows) < 1:
                print("QUERY WARNING - No rows returned.")
                return WARNING
            try:
                numeric = float(rows[0])
                if args.query_warning and not val_in_threshold(
                    args.query_warning, numeric
                ):
                    print("QUERY WARNING - ", end="")
                    state = WARNING
                elif args.query_critical and not val_in_threshold(
                    args.query_critical, numeric
                ):
                    print("QUERY CRITICAL - ", end="")
                    state = CRITICAL
                else:
                    print("QUERY OK - ", end="")
                    state = OK

                print(
                    f"'{args.query}' returned {numeric}"
                    f"|{args.query_warning if args.query_warning else ''};"
                    f"{args.query_critical if args.query_critical else ''};;"
                )

                if len(cursor.description) > 1:
                    extra_info = rows[1]
                    if extra_info:
                        print(f"Extra info: {extra_info}")
                return state

            except ValueError:
                print(f"QUERY CRITICAL - Is not a numeric: {rows[0]}")
                return CRITICAL

    except psycopg2.Error as e:
        print(f"QUERY CRITICAL - Error with Query: {e}")
        return CRITICAL


def main():
    args = get_args()

    query_status = UNKNOWN
    connection_args = {
        "database": args.database,
        "host": args.host,
        "port": args.port,
        "connect_timeout": args.timeout,
    }
    if args.logname:
        connection_args["user"] = args.logname
    if args.password:
        connection_args["password"] = args.password
    if args.option:
        connection_args["options"] = args.option

    try:
        con_start_time = time.time()
        with psycopg2.connect(**connection_args) as conn:
            con_end_time = time.time()

            elapsed_time = con_end_time - con_start_time
            if elapsed_time > args.critical:
                status = CRITICAL
            elif elapsed_time > args.warning:
                status = WARNING
            else:
                status = OK

            print(
                f"{status} check_pgsql - database {args.database} ({elapsed_time:.2f} "
                f"sec.)|{args.warning};{args.critical};;"
            )

            if args.query:
                query_status = do_query(conn, args)

            return query_status if args.query and query_status > status else status

    except psycopg2.Error as e:
        print(f"{CRITICAL} check_pgsql - connection to {args.database} failed ({e}).")
        return CRITICAL


if __name__ == "__main__":
    sys.exit(main())
