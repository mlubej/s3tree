import re
import subprocess
from typing import List

import boto3
import click


def parse_s3url(s3url: str) -> List[str]:
    s3url = s3url.replace("s3://", "")
    s3url = s3url if s3url.endswith("/") else s3url + "/"
    assert s3url != "", "S3 bucket path must be provided!"

    return s3url.split("/", maxsplit=1)


def process_list(object_list: List[str], pattern: str, ignore_pattern: str) -> List[str]:
    if pattern != "":
        object_list = [obj for obj in object_list if re.search(pattern, obj.split("/")[-1])]

    if ignore_pattern != "":
        object_list = [obj for obj in object_list if not re.search(ignore_pattern, obj.split("/")[-1])]

    return object_list


def recursive_listdir(
    client: boto3.client,
    bucket: str,
    depth: int,
    limit: int,
    pattern: str,
    ignore_pattern: str,
    prefix: str = "",
    global_list: List[str] = [],
    global_level: int = 0,
) -> List[str]:

    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter="/", MaxKeys=limit)

    if "Contents" in response:
        object_list = [c["Key"] for c in response["Contents"] if c != prefix]
        object_list = process_list(object_list, pattern, ignore_pattern)
        global_list.extend(object_list)

    if "CommonPrefixes" in response:
        object_list = [r["Prefix"] for r in response["CommonPrefixes"]]
        object_list = process_list(object_list, pattern, ignore_pattern)
        global_list.extend(object_list)

        for entry in object_list:
            if global_level < depth - 1:
                deeper_list = recursive_listdir(
                    client, bucket, depth, limit, pattern, ignore_pattern, entry, global_list, global_level + 1
                )
                global_list.extend(deeper_list)

    return global_list


@click.command()
@click.argument("s3url", default="")
@click.option("--depth", "-d", default=3, type=int, help="Depth of the recursive walk.")
@click.option("--profile", "-p", type=str, help="AWS profile name.")
@click.option("--limit", "-l", default=10, type=int, help="Limit results per AWS request in recursion step.")
@click.option("--pattern", "-P", type=str, default="", help="List only those files that match the wild-card pattern.")
@click.option(
    "--ignore_pattern", "-I", type=str, default="", help="Do not list those files that match the wild-card pattern."
)
@click.option(
    "--prune",
    is_flag=True,
    default=False,
    help="Makes tree prune empty directories from the output, useful when used in conjunction with -P or -I.",
)
@click.option(
    "--kwargs",
    default="",
    type=str,
    help=(
        "Extra parameters provided to the `tree` command. Only make sense for the usecase with the `--fromfile .`"
        " option."
    ),
)
def s3tree(
    s3url: str, depth: int, profile: str, limit: int, pattern: str, ignore_pattern: str, prune: bool, kwargs: List[str]
) -> None:

    bucket_name, prefix, *_ = parse_s3url(s3url)
    session = boto3.Session(profile_name=profile)
    client = session.client("s3")

    object_list = recursive_listdir(client, bucket_name, depth, limit, pattern, ignore_pattern, prefix)
    object_list = [key[len(prefix) :] for key in object_list]
    output = "\n".join(object_list)

    prune_option = "--prune" if prune else ""
    subprocess.call(f"echo '{output}' | tree --fromfile . {prune_option} {kwargs}", shell=True)


if __name__ == "__main__":
    s3tree()
