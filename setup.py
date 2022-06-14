import os

from setuptools import find_packages, setup


def parse_requirements(file):
    with open(os.path.join(os.path.dirname(__file__), file), mode="r", encoding="ascii") as req_file:
        return [line.strip() for line in req_file if "/" not in line]


setup(
    name="s3tree",
    python_requires=">=3.8",
    version="22.06.01",
    description="Recursive tree utility for AWS S3",
    author="Matic Lubej",
    author_email="lubej.matic@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=parse_requirements("requirements.txt"),
    extras_require={"DEV": parse_requirements("requirements-dev.txt")},
    scripts=["bin/s3tree"],
)
