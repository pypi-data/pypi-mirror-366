#!/usr/bin/env python3
import sys
from subprocess import run


def main():
    result = run(
        ["/usr/bin/docker", "exec", "exabgp", "exabgpcli", "show", "adj-rib", "out"],
        text=True,
        capture_output=True,
    )
    exit_code = result.returncode
    out = result.stdout

    status = 0
    status_txt = "OK"

    if exit_code != 0 or len(out) == 0:
        status = 2
        status_txt = "CRITICAL"

    print(status_txt, end=" ")

    if len(out) != 0:
        print("-", end=" ")
        print(out)
    return status


if __name__ == "__main__":
    sys.exit(main())
