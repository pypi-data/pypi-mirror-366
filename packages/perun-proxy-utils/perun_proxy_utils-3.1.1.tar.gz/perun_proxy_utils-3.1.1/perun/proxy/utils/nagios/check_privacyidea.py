#!/usr/bin/env python3

import argparse
import json
import sys
import tempfile
import time

import pyotp

import requests

# nagios return codes
OK = 0
CRITICAL = 2


def get_args():
    parser = argparse.ArgumentParser(
        description="Privacyidea TOTP authentication check"
    )
    parser.add_argument(
        "--hostname",
        required=True,
        type=str,
        help="Privacyidea server hostname",
    )
    parser.add_argument(
        "--username",
        required=True,
        type=str,
        help="The loginname/username of the user to authenticate with.",
    )
    parser.add_argument("--pin", type=str, help="TOTP pin", default="")
    parser.add_argument(
        "--realm",
        type=str,
        help="The realm of the user to authenticate with. "
        "If the realm is omitted, the user is looked up in the default realm.",
    )
    parser.add_argument(
        "--serial-number",
        type=str,
        dest="serial_number",
        help="The serial number of the token.",
    )
    parser.add_argument(
        "--totp",
        type=str,
        help="secret key (seed) for TOTP in Base32 encoding",
        required=True,
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="timeout for authentication request",
        default=10,
    )
    parser.add_argument(
        "--otp-only",
        action="store_true",
        dest="otp_only",
        default=False,
        help="If set, only the OTP value is verified. Only used with "
        "the parameter --serial-number.",
    )
    parser.add_argument(
        "--cache-timeout",
        type=int,
        dest="cache_timeout",
        help="specify the time after which the cache will be wiped",
        default=30,
    )
    parser.add_argument(
        "--cache-file",
        dest="cache_file",
        default="check_privacyidea_cache.txt",
        type=str,
        help="name of the file used for the cache stored in /tmp",
    )

    return parser.parse_args()


def main():
    args = get_args()

    if args.cache_timeout > 0:
        try:
            tempdir = tempfile.gettempdir()
            file_path = tempdir + "/" + args.cache_file
            with open(file_path, "r") as f:
                data = json.load(f)
                cached_time = data.get("time", time.time())
                exit_code = data.get("exit_code")
                message = data.get("message")
                time_diff = time.time() - cached_time
                if time_diff < args.cache_timeout:
                    print(f"{exit_code} check_privacyidea - Cached: {message}")
                    return exit_code
        except (OSError, ValueError):
            pass

    request_data = {
        "user": args.username,
        "type": "totp",
    }

    if args.otp_only and not args.serial_number:
        raise argparse.ArgumentTypeError(
            args.otp_only, "--otp-only cannot be used without --serial-number."
        )

    otp = pyotp.TOTP(args.totp)

    if args.realm:
        request_data["realm"] = args.realm

    if args.serial_number:
        request_data["serial"] = args.serial_number

    if args.otp_only:
        request_data["otponly"] = 1
        request_data["pass"] = otp.now()
    else:
        request_data["pass"] = args.pin + otp.now()

    try:
        response = requests.post(
            f"https://{args.hostname}/validate/check",
            json=request_data,
            timeout=args.timeout,
        )
        if response.status_code == 200:
            result = response.json().get("result")
            if not result.get("status"):
                exit_code = CRITICAL
                result_msg = "Server has problem."
            elif not result.get("value"):
                exit_code = CRITICAL
                result_msg = "Authentication failed."
            else:
                exit_code = OK
                result_msg = "Authentication was successful."
        else:
            exit_code = CRITICAL
            result_msg = f"Response status code was {response.status_code}."
    except requests.Timeout:
        result_msg = f"Request timed out in {args.timeout} seconds."
        exit_code = CRITICAL

    if args.cache_timeout > 0:
        file_path = tempfile.gettempdir() + "/" + args.cache_file
        with open(file_path, "w") as f:
            f.write(
                json.dumps(
                    {"time": time.time(), "exit_code": exit_code, "message": result_msg}
                )
            )
    print(f"{exit_code} check_privacyidea - {result_msg}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
