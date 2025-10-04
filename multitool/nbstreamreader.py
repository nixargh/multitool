"""Non blocking stream reader. Useful to read from subprocess PIPE."""

from threading import Thread
from queue import Queue, Empty


class NonBlockingStreamReader:  # pylint: disable=too-few-public-methods
    """Non blocking stream reader. Useful to read from subprocess PIPE."""

    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''

        self.stream = stream
        self.queue = Queue()

        def _populate_queue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'queue'.
            '''

            while True:
                line = stream.readline()
                if line:
                    queue.put(line)

        self.thread = Thread(
            target=_populate_queue,
            args=(self.stream, self.queue))
        self.thread.daemon = True
        self.thread.start()  # start collecting lines from the stream

    def readline(self, timeout=None):
        """Read line from stream and paste into queue."""
        block = bool(timeout)

        try:
            return self.queue.get(block, timeout=timeout)
        except Empty:
            return None
