# s3tree

A simple utility to recursively walk the AWS S3 structure and report the in the tree format, written in python.

Not tested for Windows, feel free to contribute.

## Requirements

`s3tree` doesn't attempt to create a tree from scratch, but rather uses the existing functionality from the `tree` system package, so this is a requirement, which can be installed using the links below:

|OS|Link|
|-|-|
|Linux|http://mama.indstate.edu/users/ice/tree/|
|macOS|https://formulae.brew.sh/formula/tree|

## Usage

```sh
s3tree s3://bucket-name/dir/subdir/
```

```


### More complex examples

TBA