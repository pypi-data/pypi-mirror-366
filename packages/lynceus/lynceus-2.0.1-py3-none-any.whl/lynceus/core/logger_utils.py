import logging
from logging import StreamHandler


class FilteredStdoutLoggerHandler(StreamHandler):
    """
    A specialized StreamHandler that filters log messages for stdout output.

    This handler automatically filters out WARNING level and higher messages
    to prevent duplicate log entries when using separate handlers for stdout
    and stderr. Messages with WARNING level or higher should be directed to
    stderr to maintain proper log separation.

    Inherits from logging.StreamHandler and adds automatic filtering to ensure
    only INFO, DEBUG, and TRACE level messages are sent to stdout.
    """

    def __init__(self, stream=None):
        """
        Initialize the filtered stdout logger handler.

        Parameters
        ----------
        stream : optional
            Optional stream to write to. If None, defaults to sys.stdout

        Notes
        -----
        Automatically adds a filter to exclude WARNING level and higher messages
        from being written to the output stream.
        """
        super().__init__(stream=stream)

        # Adds automatically filter to NOT log messages from Warning to more, which should be logged on stderr, and not stdout to avoid duplicates.
        self.addFilter(lambda record: record.levelno < logging.WARNING)
