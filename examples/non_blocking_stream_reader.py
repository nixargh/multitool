#!/usr/bin/env python3
"""Script to run some shell comand with interactive output."""

import logging
import sys
import time
import threading

from subprocess import Popen, PIPE  # nosec

from multitool.nbstreamreader import NonBlockingStreamReader as NBSR
from multitool.misc import lock, die, configure_logger, read_yaml_config

NAME = 'catapult'
CMD = sys.argv[1]

LOG = logging.getLogger(NAME)


class Catapult():  # pylint: disable=too-few-public-methods
    """Launch any piece of... well, of candy, using subprocess.
    Log it's stdout & stderr almost interactevly and check it's exit code.
    """

    def run(self, command, period=5, shrink=None):
        """Execute any shell command using subprocess with shell=True."""
        if shrink:
            LOG.info(
                "Starting subprocess: '%s'... (Output shrunk to %s symbols).",
                command[:shrink],
                shrink)
        else:
            LOG.info("Starting subprocess: '%s'.", command)
        try:
            process = Popen(  # pylint: disable=consider-using-with
                command,
                shell=True,  # nosec
                executable='/bin/bash',
                stdout=PIPE,
                stderr=PIPE,
                bufsize=-1,
                universal_newlines=True)
        except OSError as error:
            LOG.error("Subprocess failed: %s.", error)
        except ValueError as error:
            LOG.error("Invalid arguments for subprocess: %s.", error)

        nbsr_out = NBSR(process.stdout)
        nbsr_err = NBSR(process.stderr)
        outputs = [(nbsr_out, LOG.info), (nbsr_err, LOG.error)]

        while True:
            self._log_outputs(outputs)
            returncode = process.poll()
            if returncode is None:
                time.sleep(period)
                LOG.debug("Subprocess is running (pid=%i).", process.pid)
            else:
                LOG.debug("Subprocess returned code: %s", returncode)
                return returncode

    def _log_outputs(self, outputs):
        """Start stdout & stderr loggers in threads."""
        threads = []
        for output in outputs:
            thread = threading.Thread(target=self._log_output, args=output)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def _log_output(self, stream, log):
        """Read stream and send to logger."""
        while True:
            line = stream.readline()
            if line:
                log("[subprocess] %s", line.strip())
            else:
                break


def main():
    """Entry point."""
    configure_logger(log_level="info", filter_by=[NAME, "multitool"])
    if lock(NAME, 5):
        LOG.info("Starting %s.", NAME)

        cat = Catapult()
        cat.run(command=CMD)
    else:
        die("Locked")


if __name__ == '__main__':
    main()
