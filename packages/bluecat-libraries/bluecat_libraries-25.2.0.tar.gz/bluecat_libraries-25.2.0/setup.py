# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Setup script for bluecat-libraries."""

from pathlib import Path
from setuptools import setup, find_packages

# IMPORTANT:
# When installing as editable, it doesn't matter what the current directory is when invoking
# `pip install -e <path-to-bclib>`, but when building a package, current directory has to be `HERE`.
HERE = Path(__file__).resolve().parent


def get_version() -> str:
    """Self-explanatory."""
    fp = HERE / "version.txt"
    if fp.exists():
        v = fp.read_text().strip()
    else:
        v = "0.0.0+placeholder"
    # print(f"The version for the package is going to be: {v}")
    return v


setup(
    name="bluecat-libraries",
    version=get_version(),
    author="BlueCat",
    maintainer="BlueCat",
    url="https://docs.bluecatnetworks.com",
    description="Modules for working with BlueCat products.",
    long_description=(HERE / "README.rst").read_text(),
    long_description_content_type="text/x-rst",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    python_requires=">=3.11.0",
    package_dir={"": "src"},  # does not accept abs path
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.32.4",
    ],
    extras_require={
        "dev": [
            "pytest==7.3.0",
            "responses==0.23.1",
            "paramiko==3.0.0",
        ],
        "internal-suds": [
            "suds-py3==1.4.5.0",
        ],
    },
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
    ],
)
