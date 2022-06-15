import re
from typing import List

import boto3
import click

SPACE = "    "
BRANCH = "│   "
TEE = "├── "
LAST = "└── "
DIR_COLOR = "\033[94m"
END_COLOR = "\033[0m"


def parse_s3url(s3url: str) -> List[str]:
    s3url = s3url.replace("s3://", "")
    s3url = s3url if s3url.endswith("/") else s3url + "/"
    assert s3url != "", "S3 bucket path must be provided!"

    return s3url.split("/", maxsplit=1)


def process_list(object_list: List[str], pattern: str, i_pattern: str) -> List[str]:
    new_object_list = []
    for obj in object_list:
        if obj.endswith("/"):
            new_object_list.append(obj)
            continue

        f_name = obj.split("/")[-1]
        pattern_condition = True if pattern == "" else re.search(pattern, f_name)
        i_pattern_condition = False if i_pattern == "" else re.search(i_pattern, f_name)

        if pattern_condition and not i_pattern_condition:
            new_object_list.append(obj)
    return new_object_list


def tree(
    client: boto3.client,
    bucket: str,
    depth: int,
    limit: int,
    pattern: str,
    i_pattern: str,
    prune: bool,
    prefix: str = "",
    extension: str = "",
    level: int = 0,
) -> None:

    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter="/", MaxKeys=limit + 1)
    object_list = []
    if "CommonPrefixes" in response:
        object_list.extend([r["Prefix"] for r in response["CommonPrefixes"]])
    if "Contents" in response:
        object_list.extend([c["Key"] for c in response["Contents"] if c["Key"] != prefix])
    object_list = process_list(object_list, pattern, i_pattern)

    if response["IsTruncated"]:
        object_list.append(prefix + "...")

    pointers = [TEE] * (len(object_list) - 1) + [LAST]
    for pointer, path in zip(pointers, object_list):
        out = path.replace(prefix, "")
        is_dir = out.endswith("/")
        out = f"{DIR_COLOR}{out}{END_COLOR}" if is_dir else out

        if prune and level == depth - 1 and is_dir:
            continue
        else:
            print(extension + pointer + out)

        if level < depth - 1:
            pre_ext = BRANCH if pointer == TEE else SPACE
            tree(client, bucket, depth, limit, pattern, i_pattern, prune, path, pre_ext + extension, level + 1)


@click.command()
@click.argument("s3url", default="")
@click.option("--depth", "-d", default=3, type=int, help="Depth of the recursive walk.")
@click.option("--profile", "-p", type=str, help="AWS profile name.")
@click.option("--limit", "-l", default=10, type=int, help="Limit results per AWS request in recursion step.")
@click.option("--pattern", "-P", type=str, default="", help="List only those files that match the wild-card pattern.")
@click.option(
    "--i_pattern", "-I", type=str, default="", help="Do not list those files that match the wild-card pattern."
)
@click.option(
    "--prune",
    is_flag=True,
    default=False,
    help="Makes tree prune empty directories from the output, useful when used in conjunction with -P or -I.",
)
def s3tree(s3url: str, depth: int, profile: str, limit: int, pattern: str, i_pattern: str, prune: bool) -> None:

    bucket_name, prefix, *_ = parse_s3url(s3url)
    session = boto3.Session(profile_name=profile)
    client = session.client("s3")

    print(f"{DIR_COLOR}{s3url}{END_COLOR}")
    tree(client, bucket_name, depth, limit, pattern, i_pattern, prune, prefix)


if __name__ == "__main__":
    s3tree()
