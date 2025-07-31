#!/usr/bin/env python3

import gzip
import shutil
import re
import sys
from os import mkdir, path, rename, remove, system
import argparse


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(
        description="Script removes all logs from test accounts from SimpleSAMLphp logs."
    )
    parser.add_argument("filename", help="The file name of log file")
    return parser.parse_args()


def main():
    absolute_file_name = get_args().filename

    if not path.exists(absolute_file_name):
        print("File with name " + absolute_file_name + " doesn't exists!")
        sys.exit(-1)

    file_name = path.basename(absolute_file_name)
    dir_name = path.dirname(absolute_file_name)

    if len(dir_name) != 0:
        dir_name += "/"

    full_log_dir_name = dir_name + "full_logs/"
    full_log_file_name = "full_" + file_name
    full_log_absolute_name = full_log_dir_name + full_log_file_name

    if not path.exists(full_log_dir_name):
        mkdir(full_log_dir_name)

    rename(absolute_file_name, full_log_absolute_name)

    session_ids = set()
    thread_ids = set()
    regex_session_id = r"^.*]:\s\d\s\[(.*?)\].*$"
    regex_thread_id = r"^.*\[(.*?)\]:.*$"

    file = open(full_log_absolute_name, "r")
    for line in file:
        res = re.search("proxyidptester@cesnet.cz|9006464@muni.cz", line)
        if res is not None:
            session_id = re.search(regex_session_id, line)
            if session_id is not None:
                session_ids.add(session_id.group(1))
            thread_id = re.search(regex_thread_id, line)
            if thread_id is not None:
                thread_ids.add(thread_id.group(1))
    file.close()

    file = open(full_log_absolute_name, "r")

    final_log_file = open(absolute_file_name, "w")
    last_session_id = ""
    for line in file:
        session_id = re.search(regex_session_id, line)
        if session_id is not None:
            last_session_id = session_id.group(1)
        if session_id is None or session_id.group(1) not in session_ids:
            thread_id = re.search(regex_thread_id, line)
            if (
                thread_id is None
                or thread_id.group(1) not in thread_ids
                or last_session_id not in session_ids
            ):
                final_log_file.write(line)

    file.close()
    final_log_file.close()

    # Zip old log file
    with (
        open(full_log_absolute_name, "rb") as f_in,
        gzip.open(full_log_absolute_name + ".gz", "wb") as f_out,
    ):
        shutil.copyfileobj(f_in, f_out)

    # Remove unzip file
    remove(full_log_absolute_name)

    # Remove old files
    system("find " + full_log_dir_name + " -mtime +7 -delete")


if __name__ == "__main__":
    main()
