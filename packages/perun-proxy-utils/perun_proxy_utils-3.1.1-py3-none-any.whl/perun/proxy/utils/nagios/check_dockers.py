#!/usr/bin/env python3

import argparse
import sys

import docker
from docker.errors import NotFound, APIError


def get_docker_states(req_containers):
    client = docker.from_env()
    containers = {}
    for item in req_containers:
        try:
            container = client.containers.get(item)
            containers[container.name] = container.status
        except (NotFound, APIError):
            containers[item] = "ERROR"

    return containers


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description="Check dockers")
    parser.add_argument(
        "-c",
        "--containers",
        required=True,
        help="list of container names to check in following"
        "format: '['cont1', 'cont2']'",
    )

    return parser.parse_args()


def main():
    args = get_args()
    containers_list = args.containers.replace(" ", "").strip("[]").split(",")
    containers_list = [container_name.strip("'") for container_name in containers_list]
    containers_status = get_docker_states(containers_list)

    status = 0
    status_info = ""

    for container_name in containers_status:
        container_status = containers_status[container_name]
        if container_status != "running":
            status = 2
        status_info += container_name + ": " + container_status + "; "

    print(str(status) + " docker_containers - [" + status_info + "]")
    return status


if __name__ == "__main__":
    sys.exit(main())
