# -*- coding: utf-8 -*-

import codecs
import os.path
import re
import setuptools


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="conda_tools",
    version=find_version("conda_tools", "__init__.py"),
    author="Jeremy Jacobs",
    author_email="pub@j4c0bs.net",
    description="Conda env utilities.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/j4c0bs/conda-env-tools",
    packages=setuptools.find_packages(),
    install_requires=["oyaml"],
    include_package_data=False,
    classifiers=[],
    entry_points={"console_scripts": ["conda_tools=conda_tools.cli:run_cli"]},
)
