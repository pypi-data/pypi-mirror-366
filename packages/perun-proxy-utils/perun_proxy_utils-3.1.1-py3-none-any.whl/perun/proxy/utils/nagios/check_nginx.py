#!/usr/bin/env python3
import sys

from check_nginx_status.check_nginx_status import main

# for program arguments check
# https://gitlab.ics.muni.cz/perun/deployment/proxyidp/check_nginx_status

if __name__ == "__main__":
    sys.exit(main())
