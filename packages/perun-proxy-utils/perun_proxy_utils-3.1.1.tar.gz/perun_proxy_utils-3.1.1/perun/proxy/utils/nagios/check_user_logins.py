#!/usr/bin/env python3

import argparse
import datetime
import sys
import re

# nagios return codes
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2


def parse_log_data(log_path, regex, date_format):
    file = open(log_path, "r", encoding="utf-8")
    lines = file.readlines()
    user_dict = {}
    for line in lines:
        result = re.match(regex, line)
        if result:
            user_id = result.group("userid")
            if user_id not in user_dict.keys():
                user_dict[user_id] = [
                    datetime.datetime.strptime(
                        result.group("datetime"), date_format
                    ).timestamp()
                ]
            else:
                user_dict[user_id].append(
                    datetime.datetime.strptime(
                        result.group("datetime"), date_format
                    ).timestamp()
                )
    return user_dict


def check_log_data(user_dict, limits, seconds):
    warning = False
    for user, date_times in user_dict.items():
        final_count = 0
        count = 0
        date_times.sort()
        for check_date_time in range(len(date_times)):
            for i in range(len(date_times)):
                if check_date_time <= i:
                    if date_times[i] - date_times[check_date_time] <= seconds:
                        count += 1
                    else:
                        break
            if final_count < count:
                final_count = count
            count = 0

        if final_count > limits:
            print("WARNING - User: {} logins count: {}".format(user, final_count))
            warning = True
    if warning:
        sys.exit(WARNING)


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def command_line_validate(argv):
    parser = argparse.ArgumentParser(description="frequent login check")
    parser._optionals.title = "Options"
    parser.add_argument(
        "--path",
        "-p",
        required=True,
        help="path to log file",
    )
    parser.add_argument(
        "--regex",
        "-r",
        required=True,
        help="parsing regex of logfile, must include groups userid and datetime",
    )
    parser.add_argument(
        "--datetime_format",
        "-d",
        required=True,
        help="datetime format of log file",
    )
    parser.add_argument(
        "--logins",
        "-l",
        type=check_positive,
        required=True,
        help="maximal number of logins",
    )
    parser.add_argument(
        "--seconds",
        "-s",
        type=check_positive,
        required=True,
        help="time interval for logins check",
    )
    args = parser.parse_args()
    return args.path, args.regex, args.datetime_format, args.logins, args.seconds


def main():
    argv = sys.argv[1:]
    path, regex, datetime_format, logins, seconds = command_line_validate(argv)
    user_dict = parse_log_data(path, regex, datetime_format)
    check_log_data(user_dict, logins, seconds)
    print("OK - ", logins, seconds)
    sys.exit(0)


if __name__ == "__main__":
    main()
