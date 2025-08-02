"""Python dual-logging setup (console and log file).

It supports different log levels and colorized output.

Created by Fonic <https://github.com/fonic>
Date: 04/05/20 - 02/07/23

Based on:
https://stackoverflow.com/a/13733863/1976617
https://uran198.github.io/en/python/2016/07/12/colorful-python-logging.html
https://en.wikipedia.org/wiki/ANSI_escape_code#Colors

.. todo::
    Modernize this, with type hint etc.

"""

import logging
import sys
from collections.abc import Collection, Iterator
from contextlib import contextmanager
from pathlib import Path


class LogFormatter(logging.Formatter):
    """Logging formatter supporting colorized output."""

    COLOR_CODES = {
        logging.CRITICAL: "\033[1;35m",  # bright/bold magenta
        logging.ERROR: "\033[1;31m",  # bright/bold red
        logging.WARNING: "\033[1;33m",  # bright/bold yellow
        logging.INFO: "\033[0;37m",  # white / light gray
        logging.DEBUG: "\033[1;30m",  # bright/bold black / dark gray
    }

    RESET_CODE = "\033[0m"

    def __init__(self, color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color

    def format(self, record, *args, **kwargs):
        if self.color == True and record.levelno in self.COLOR_CODES:
            record.color_on = self.COLOR_CODES[record.levelno]
            record.color_off = self.RESET_CODE
        else:
            record.color_on = ""
            record.color_off = ""
        return super().format(record, *args, **kwargs)


class SuppressMessageFilter(logging.Filter):
    """Filter to temporarily suppress some logs."""

    def __init__(self, suppressed_substrings: Collection[str]) -> None:
        """Set the list of log messages to remove.

        Parameters
        ----------
        suppressed_substrings :
            Substrings to match against log messages. Any log containing one of
            these will be suppressed.

        """
        self.substrings = list(suppressed_substrings)

    def filter(self, record: logging.LogRecord) -> bool:
        """Determine if the specified record is to be logged.

        Parameters
        ----------
        record :
            The log record to be evaluated.

        Returns
        -------
        bool
            False if the message contains one of the suppressed substrings;
            True otherwise.

        """
        return not any(
            substr in record.getMessage() for substr in self.substrings
        )


@contextmanager
def suppress_log_messages(
    logger_name: str, substrings: list[str]
) -> Iterator[None]:
    """
    Temporarily suppress log messages that contain any of the given substrings.

    Parameters
    ----------
    logger_name :
        Name of the logger to apply the filter to. Use "" for the root logger.
    substrings :
        Substrings to match against log messages. Messages containing any of
        these substrings will be suppressed.

    Yields
    ------
    None
        Yields control to the context block with the filter active.

    """
    logger = logging.getLogger(logger_name)
    filt = SuppressMessageFilter(substrings)
    logger.addFilter(filt)
    try:
        yield
    finally:
        logger.removeFilter(filt)


def set_up_logging(
    console_log_output="stdout",
    console_log_level="INFO",
    console_log_color=True,
    console_log_line_template="%(color_on)s[%(levelname)-8s] [%(filename)-20s]%(color_off)s %(message)s",
    logfile_file=Path("multipac_testbench.log"),
    logfile_log_level="INFO",
    logfile_log_color=False,
    logfile_line_template="%(color_on)s[%(asctime)s] [%(levelname)-8s] [%(filename)-20s]%(color_off)s %(message)s",
):
    """Set up logging."""
    # Remove previous logger
    del logging.root.handlers[:]
    # Create logger
    # For simplicity, we use the root logger, i.e. call 'logging.getLogger()'
    # without name argument. This way we can simply use module methods for
    # for logging throughout the script. An alternative would be exporting
    # the logger, i.e. 'global logger; logger = logging.getLogger("<name>")'
    logger = logging.getLogger()

    # Set global log level to 'debug' (required for handler levels to work)
    logger.setLevel(logging.DEBUG)

    # Create console handler
    console_log_output = console_log_output.lower()
    if console_log_output == "stdout":
        console_log_output = sys.stdout
    elif console_log_output == "stderr":
        console_log_output = sys.stderr
    else:
        print(
            "Failed to set console output: invalid output: '%s'"
            % console_log_output
        )
        return False
    console_handler = logging.StreamHandler(console_log_output)

    # Set console log level
    try:
        # only accepts uppercase level names
        console_handler.setLevel(console_log_level.upper())
    except:
        print(
            "Failed to set console log level: invalid level: '%s'"
            % console_log_level
        )
        return False

    # Create and set formatter, add console handler to logger
    console_formatter = LogFormatter(
        fmt=console_log_line_template, color=console_log_color
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Create log file handler
    try:
        logfile_handler = logging.FileHandler(logfile_file)
    except Exception as exception:
        print("Failed to set up log file: %s" % str(exception))
        return False

    # Set log file log level
    try:
        # only accepts uppercase level names
        logfile_handler.setLevel(logfile_log_level.upper())
    except:
        print(
            "Failed to set log file log level: invalid level: '%s'"
            % logfile_log_level
        )
        return False

    # Create and set formatter, add log file handler to logger
    logfile_formatter = LogFormatter(
        fmt=logfile_line_template, color=logfile_log_color
    )
    logfile_handler.setFormatter(logfile_formatter)
    logger.addHandler(logfile_handler)

    return True


def main():
    """Main function."""

    if not set_up_logging():
        print("Failed to set up logging, aborting.")
        return 1

    logging.debug("Debug message")
    logging.info("Info message")
    logging.warning("Warning message")
    logging.error("Error message")
    logging.critical("Critical message")


if __name__ == "__main__":
    sys.exit(main())
