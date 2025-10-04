"""Miscellaneous functions."""

import socket
import time
import logging
import logging.handlers
import os
from ipaddress import IPv4Address, IPv4Network
import yaml

from .logging import configure_logger as _configure_logger
from . import __version__


class MultitoolDie(Exception):
    """Common exception of multitool."""


def configure_logger(*args, **kwargs):
    """Stub function for backward compatibility."""
    return _configure_logger(*args, **kwargs)


def lock(name, timeout=30):
    """Lock using unix socket."""
    # Without holding a reference to our socket somewhere it gets garbage
    # collected when the function exits
    lock._lock_socket = socket.socket(  # pylint: disable=protected-access
        socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        lock._lock_socket.bind('\0' + name)  # pylint: disable=protected-access
        return True
    except OSError:
        time.sleep(timeout)
        try:
            lock._lock_socket.bind(  # pylint: disable=protected-access
                '\0' + name)
            return True
        except socket.error:
            return False


def die(message):
    """Log error message and raise exception with the same message."""
    logger = logging.getLogger(__name__)
    logger.error("%s.", message)
    raise MultitoolDie(message)


def read_yaml_config(config_file):
    """Read YAML file and return its content."""
    logger = logging.getLogger(__name__)
    logger.debug("Loading configuration from %s.", config_file)
    dicts = []
    try:
        with open(
                os.path.realpath(os.path.expanduser(config_file)),
                "r",
                encoding="utf8") as yaml_file:
            documents = yaml.load_all(yaml_file, Loader=yaml.FullLoader)
            for document in documents:
                dicts.append(document)
        if len(dicts) > 1:
            return dicts
        return dicts[0]
    except IOError as error:
        logger.error(
            "Failed to read config file: [%s] %s.",
            error.errno,
            error.strerror)
        return None
    except yaml.parser.ParserError as error:
        logger.error("Config isn't a valid YAML. Error: %s.", error)
        return None


def ip_belongs_to(address, networks):
    """
    Check whether IP address belongs to one of networks.

    :type address: str
    :param address: An IP address.

    :type networks: list, tuple or set of str
    :param networks: A list of IP ranges.

    :rtype: str
    :return: None or IP range that address belongs to.
    """
    for ip_range in networks:
        ip_network = IPv4Network(ip_range)
        ip_address = IPv4Address(address)
        if ip_address in ip_network:
            return ip_range
    return None
