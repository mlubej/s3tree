# s3tree

A simple utility to recursively walk the AWS S3 structure and report the in the tree format, written in python.

Not tested for Windows, feel free to contribute.

## Arguments and Options

```sh
s3tree --help
Usage: s3tree [OPTIONS] [S3URL]

Options:
  -d, --depth INTEGER        Depth of the recursive walk.
  -p, --profile TEXT         AWS profile name.
  -l, --limit INTEGER        Limit results per AWS request in recursion step.
  -P, --pattern TEXT         List only those files that match the wild-card
                             pattern.
  -I, --ignore_pattern TEXT  Do not list those files that match the wild-card
                             pattern.
  --prune                    Makes tree prune empty directories from the
                             output, useful when used in conjunction with -P
                             or -I.
  --help                     Show this message and exit.
```


## Usage

```sh
s3tree s3://bucket-name/dir/subdir/
```

### More complex examples

Define specific depth

```sh
s3tree s3://bucket-name/dir/subdir/ -d 4
```

Show only files starting with 0

```sh
s3tree s3://bucket-name/dir/subdir/ -P '^0'
```

Ignore files ending with `.json`, use specific AWS profile, prune last level

```sh
s3tree s3://bucket-name/dir/subdir/ -I '.json$' --profile my_profile --prune
```

## Example output

```sh
s3tree s3://my_s3_bucket/dir/subdir/ -d 4 -l 3 -I '.gz$'
s3://my_s3_bucket/dir/subdir/
├── dir1/
│   ├── dir2/
│   │   ├── dir3/
│   │   │   └── ...
│   │   ├── dir4/
│   │   ├── dir5/
│   │   └── ...
│   └── ...
├── file1.ext
├── file2.ext
├── file3.ext
└── ...
```