"""LIbrary to handle Python logging configuration."""

import sys
import os
import logging
import logging.handlers


class TechopslibLoggingError(Exception):
    """Common exception of multitool.logging."""


def configure_logger(  # noqa pylint: disable=too-many-arguments,too-many-positional-arguments
        log_level="INFO",
        log_file=None,
        stream=sys.stdout,
        filter_by=None,
        thread_name=False,
        reopen=True,
        self_managed=False):
    """Configure root logger.

    :type log_level: str
    :param log_level: (Optional) Logging level. Default is INFO.

    :type log_file: str
    :param log_file: (Optional) Path to log file. Default is None.

    :type stream: stream object
    :param stream: (Optional) any file-like object (or, more precisely,
                   any object which supports write() and flush() methods).
                   Default is sys.stdout.

    :type filter_by: str, list
    :param filter_by: (Optional) Logger names or parts of names to show
                     message from. Default is None.

    :type thread_name: bool
    :param thread_name: (Optional) Show name of thread or not.
                        Default is False.

    :type reopen: bool
    :param reopen: (Optional) Re-open rotated log file. Default is True.

    :type self_managed: bool
    :param reopen: (Optional) Manage log file rotation. Default is False.
    """

    return_handler = None

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Ask one or multiple handlers depending on number of filters
    ftype = type(filter_by)
    if not filter_by or ftype == str:
        handler = _configure_handler(
            log_file=log_file,
            stream=stream,
            filter_by=filter_by,
            thread_name=thread_name,
            watched=reopen,
            timed=self_managed)
        logger.addHandler(handler)
    elif ftype == list:
        for onefilter in filter_by:
            handler = _configure_handler(
                log_file=log_file,
                stream=stream,
                filter_by=onefilter,
                thread_name=thread_name,
                watched=reopen,
                timed=self_managed)
            logger.addHandler(handler)
    else:
        message = "Logger configuration failed. " \
                f"Unknown 'filter_by' type: {ftype}"
        raise TechopslibLoggingError(message)

    logger.debug("Logger configured. Severity: %s.", log_level.upper())
    return return_handler


def _configure_handler(  # noqa pylint: disable=too-many-arguments,too-many-positional-arguments
        log_file=None,
        stream=sys.stdout,
        filter_by=None,
        thread_name=False,
        watched=True,
        timed=False):
    """Configure logging handler.

    :type log_file: str
    :param log_file: (Optional) Path to log file. Default is None.

    :type stream: stream object
    :param stream: (Optional) any file-like object (or, more precisely,
                   any object which supports write() and flush() methods).
                   Default is sys.stdout.

    :type filter_by: str
    :param filter_by: (Optional) Logger name or a part of name to show
                      message from. Default is None.

    :type thread_name: bool
    :param thread_name: (Optional) Show name of thread or not.
                        Default is False.

    :type watched: bool
    :param watched: (Optional) Use WatchedFileHandler or just FileHandler.
                    Conflicts with 'timed'.
                    Default is True.

    :type timed: bool
    :param watched: (Optional) Use TimedRotatingFileHandler
                    or just FileHandler. Conflicts with 'watched'.
                    Default is False.

    :rtype: logging.handler
    :return: Some logging handler depending on given arguments.
    """
    # Resolve options conflict
    if watched and timed:
        raise ValueError(
            "Logging handler can't be 'watched' and 'timed' at the same time")

    # Choose between stdout and file
    if log_file:
        log_dir = os.path.dirname(log_file)
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        if timed:
            handler = logging.handlers.TimedRotatingFileHandler(
                log_file,
                when="midnight",
                backupCount=14)
        elif watched:
            handler = logging.handlers.WatchedFileHandler(log_file)
        else:
            handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler(stream)

    # Log output format
    if thread_name:
        formatter = logging.Formatter(
            "%(asctime)s %(process)-8d %(name)-35s "
            "%(levelname)-8s [%(threadName)s]: %(message)s")
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(process)-8d %(name)-35s "
            "%(levelname)-8s %(message)s")
    handler.setFormatter(formatter)

    # Add filter
    if filter_by:
        lfilter = logging.Filter(filter_by)
        handler.addFilter(lfilter)

    return handler
