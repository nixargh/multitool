#!/usr/bin/env python3
"""Script to read config from YAML."""

import logging
import sys

from multitool.misc import lock, die, configure_logger, read_yaml_config

NAME = 'read_yaml_config'
YAML_FILE = sys.argv[1]

LOG = logging.getLogger(NAME)


def main():
    """Entry point."""
    configure_logger(log_level="info", filter_by=[NAME, "multitool"])
    if lock(NAME, 5):
        LOG.info("Starting %s.", NAME)

        yaml = read_yaml_config(YAML_FILE)

        LOG.info("Config: %s.", yaml)
    else:
        die("Locked")


if __name__ == '__main__':
    main()
