import sys
import argparse
from urllib.request import urlopen
from bs4 import BeautifulSoup


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(
        description="This script checks whether there are some metadata close to expiration date."
    )
    parser.add_argument(
        "url",
        help="url to a page which prints a time when expires the metadata closest to expiration",
    )
    return parser.parse_args()


def main():
    url = get_args().url
    html = urlopen(url).read()
    closest_expiration = BeautifulSoup(html, "html.parser")

    if float(closest_expiration.text) >= 24:
        print("0 metadata_expiration - OK (" + closest_expiration.text + ")")
        return 0
    elif float(closest_expiration.text) >= 12:
        print("1 metadata_expiration - WARNING (" + closest_expiration.text + ")")
        return 1
    else:
        print("2 metadata_expiration - CRITICAL (" + closest_expiration.text + ")")
        return 2


if __name__ == "__main__":
    sys.exit(main())
