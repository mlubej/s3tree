import subprocess
from typing import Tuple

import boto3
import click


def parse_s3url(s3url: str) -> Tuple[str, str]:
    s3url = s3url.replace("s3://", "")
    s3url = s3url if s3url.endswith("/") else s3url + "/"
    assert s3url != "", "S3 bucket path must be provided!"

    return s3url.split("/", 1)


def recursive_listdir(client, bucket, depth, limit, prefix="", global_list=[], global_level=0):

    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter="/", MaxKeys=limit)

    if "Contents" in response:
        object_list = [c["Key"] for c in response["Contents"] if c != prefix]
        global_list.extend(object_list)

    if "CommonPrefixes" in response:
        object_list = [r["Prefix"] for r in response["CommonPrefixes"]]
        global_list.extend(object_list)

        for entry in object_list:
            if global_level < depth - 1:
                recursive_listdir(client, bucket, depth, limit, entry, global_list, global_level + 1)

    if global_level == 0:
        return global_list


@click.command()
@click.argument("s3url", default="")
@click.option("--depth", "-d", default=1, type=int, help="Depth of the constructed tree.")
@click.option("--profile", "-p", type=str, help="AWS profile name.")
@click.option("--limit", "-l", default=10, type=int, help="Limit per recursion step.")
def s3tree(s3url, depth, profile, limit):

    bucket_name, prefix = parse_s3url(s3url)
    session = boto3.Session(profile_name=profile)
    client = session.client("s3")

    object_list = recursive_listdir(client, bucket_name, depth, limit, prefix=prefix)
    object_list = [key[len(prefix) :] for key in object_list]
    output = "\n".join(object_list)

    subprocess.call(f"echo '{output}' | tree --fromfile .", shell=True)


if __name__ == "__main__":
    s3tree()
