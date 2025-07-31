#!/usr/bin/env python3

import multiprocessing
import os
import re
import json

import docker
import argparse
import platform


def main():
    output = {
        "cpu_count": "",
        "memory": "",
        "os_version": "",
        "kernel_version": "",
        "docker_version": "",
        "containerd_version": "",
        "containers": {},
    }
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        help="Space delimited list of containers to exclude",
    )
    args = parser.parse_args()
    exc_containers = args.exclude.split(" ") if args.exclude is not None else []
    output["cpu_count"] = str(multiprocessing.cpu_count())
    mem_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    if mem_bytes > 1:
        output["memory"] = str(round(mem_bytes / (1024.0**3), 2)) + "GiB"
    name = ""
    maj_version = ""
    with open("/etc/os-release") as file:
        contents = file.read()
        match = re.search(r"NAME=\"(.*)\"", contents)
        if match is not None:
            name = match.group(1)
        match = re.search(r"VERSION_ID=\"(.*)\"", contents)
        if match is not None:
            maj_version = match.group(1).split(".")[0]
    if name.startswith("Debian"):
        name = name.split(" ")[0]
    output["os_version"] = name + " " + maj_version
    output["kernel_version"] = platform.release()
    client = docker.from_env()
    if client is not None:
        version_info = client.version()
        docker_ver_filter = list(
            filter(lambda x: x["Name"] == "Engine", version_info["Components"])
        )
        output["docker_version"] = (
            docker_ver_filter[0]["Version"] if len(docker_ver_filter) > 0 else ""
        )
        containerd_ver_filter = list(
            filter(lambda x: x["Name"] == "containerd", version_info["Components"])
        )
        containerd_version = (
            containerd_ver_filter[0]["Version"]
            if len(containerd_ver_filter) > 0
            else ""
        )
        if len(containerd_version) > 0 and containerd_version[0] == "v":
            containerd_version = containerd_version[1:]
        output["containerd_version"] = containerd_version
        containers = client.containers.list()
        containers = list(filter(lambda x: x.name not in exc_containers, containers))
        for container in containers:
            container_image = container.image.tags[0] if container.image.tags else ""
            output["containers"][container.name] = container_image.split(":")[-1]
    print(json.dumps(output))


if __name__ == "__main__":
    main()
