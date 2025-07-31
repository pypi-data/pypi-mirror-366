#!/usr/bin/env python3

import asyncio
import json

import asyncssh
import argparse


def jsons_to_dictionary(jsons, hosts):
    versions_dicts = list(map(lambda x: json.loads(x), jsons))
    ret_dict = {"hosts": hosts}
    for i in range(len(versions_dicts)):
        versions_dicts[i].update(versions_dicts[i]["containers"])
        versions_dicts[i].pop("containers")
        for key, val in versions_dicts[i].items():
            if key in ret_dict:
                ret_dict[key].append(val)
            else:
                ret_dict[key] = ["-" for _ in range(i)] + [val]
        for key, val in ret_dict.items():
            if len(val) < i + 1:
                ret_dict[key].append("-")
    return ret_dict


def dict_to_md_table(dictionary):
    keys = list(dictionary.keys())
    values = list(dictionary.values())
    lengths = [
        max(max(map(lambda x: len(x), value)), len(str(key)))
        for key, value in dictionary.items()
    ]
    keys[0] = ""
    print(
        "| "
        + " | ".join([f"{key:<{length}}" for key, length in zip(keys, lengths)])
        + " |"
    )
    print(
        "| " + " | ".join([f"{':-:':<{lengths[i]}}" for i in range(len(keys))]) + " |"
    )
    for i in range(len(values[0])):
        print(
            "| "
            + " | ".join(
                [f"{str(value[i]):<{length}}" for length, value in zip(lengths, values)]
            )
            + " |"
        )


async def run_script(user, host, exc_containers):
    try:
        async with asyncssh.connect(host, username=user) as conn:
            await asyncssh.scp("print_docker_versions.py", (conn, "/tmp/"))
            return (
                await conn.run(
                    'python3 /tmp/print_docker_versions.py -e "' + exc_containers + '"',
                ),
                host,
            )
    except Exception as e:
        return e, host


async def collect_info(hosts, exc_containers):
    tasks = (run_script(host[0], host[1], exc_containers) for host in hosts)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    stdouts = []
    hosts = []
    for result, host in results:
        if isinstance(result, Exception):
            print("Connecting to host %s failed: %s" % (host, str(result)))
        elif result.exit_status != 0:
            print(
                "Running script on %s exited with status %s:"
                % (host, result.exit_status)
            )
            print(result.stderr, end="")
        else:
            stdouts.append(result.stdout)
            hosts.append(host)
    if len(stdouts) > 0 and len(hosts) > 0:
        dict_to_md_table(jsons_to_dictionary(stdouts, hosts))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        help="Space delimited list of containers to exclude",
    )
    parser.add_argument("machines", nargs="+", help="Machines to collect the info from")

    args = parser.parse_args()
    exc_containers = args.exclude if args.exclude is not None else ""
    machines = list(map(lambda x: x.split("@"), args.machines))
    asyncio.run(collect_info(machines, exc_containers))


if __name__ == "__main__":
    main()
