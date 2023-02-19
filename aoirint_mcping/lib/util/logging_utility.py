import datetime
import logging


def setup_logging_format_time_with_timezone():
    # https://stackoverflow.com/a/58777937
    logging.Formatter.formatTime = (
        lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(
            record.created, datetime.timezone.utc
        )
        .astimezone()
        .isoformat(sep="T", timespec="milliseconds")
    )
