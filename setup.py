#!/usr/bin/env python3
"""Setup of multitool."""

import os
import re

from setuptools import setup, find_packages

NAME = "multitool"
DIST_PACKAGES = "/usr/lib/python3/dist-packages"
CONFLICTS = []
TEST_REQUREMENTS = [
    'mock',
]


def get_variable_from_file(ffile, variable):
    """Get variable from file."""
    variable_re = f"^{variable} = ['\"]([^'\"]*)['\"]"
    with open(ffile, "r", encoding="utf8") as ffile_obj:
        match = re.search(variable_re, ffile_obj.read(), re.M)
    if match:
        return match.group(1)
    return None


def get_version():
    """Get package version."""
    return get_variable_from_file(NAME + "/__init__.py", "__version__")


def get_requires(rfile):
    """Get list of required Python packages."""
    requires = []
    with open(rfile, "r", encoding="utf8") as reqfile:
        for line in reqfile.readlines():
            requires.append(line.strip())
    return requires


def add_postinstall(action):
    """Add postinstall action."""
    with open("./debian/postinst", "w", encoding="utf8") as postinst:
        postinst.write("#!/bin/bash\n")
        postinst.write(action + "\n")


def add_prerm(action):
    """Add prerm action."""
    with open("./debian/prerm", "w", encoding="utf8") as prerm:
        prerm.write("#!/bin/bash\n")
        prerm.write(action + "\n")


def add_conflicts(packages):
    """Add Conflicts:"""
    content = []

    with open("./debian/control", "r", encoding="utf8") as control:
        content = control.readlines()

    with open("./debian/control", "w", encoding="utf8") as control:
        for line in content:
            control.write(line)
            print(line)
            if re.match(r"^Depends:\s.+$", line):
                control.write(f'Conflicts: {", ".join(packages)}\n')


def set_stop():
    """Set stop mark at debian directory."""
    with open("./debian/stop", "w", encoding="utf8") as stop:
        stop.write("stopped")


def stopped():
    """Check if stopped."""
    return os.path.isfile("./debian/stop")


def get_config_dir():
    """Get configuration directory."""
    return get_variable_from_file(
        NAME + "/__init__.py",
        "CONFIG_ROOT_DIR")


def get_files(data_dir):
    """Get files from directory."""
    files = []
    for dir_file in os.listdir(data_dir):
        data_file = f"{data_dir}/{dir_file}"
        if os.path.isfile(data_file):
            files.append(data_file)
    return files


setup(
    name=NAME,
    version=get_version(),
    packages=find_packages(exclude=["tests"]),
    description='Multitool Python library',
    long_description="Libraries collection useful for everyday coding",
    author="Universe",
    author_email='dust@universe.org',
    url="https://github.com/nixargh/multitool",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    data_files=[
        (
            "/usr/share/multitool/examples",
            get_files("./examples")
        ),
    ],
    entry_points={
        'console_scripts': ['multitool = multitool:get_version']
    },
    install_requires=get_requires("./requirements.txt"),
)

if os.path.isdir('./debian') and not stopped():
    add_conflicts(CONFLICTS)
    set_stop()
