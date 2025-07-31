import time
import logging
from default_logging.millisecond_formatter import MillisecondFormatter, UtcTimezoneFormatter


def test_millisecond_formatter_format_time_with_datefmt():
    formatter = MillisecondFormatter(fmt="%(asctime)s", datefmt="%Y-%m-%dT%H:%M:%S.%f%z")
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname=__file__, lineno=1,
        msg="msg", args=(), exc_info=None
    )
    record.created = time.time()
    record.msecs = int((record.created - int(record.created)) * 1000)
    formatted_time = formatter.formatTime(record, formatter.datefmt)
    assert formatted_time.endswith(formatter.tz_str)
    assert "." in formatted_time

def test_millisecond_formatter_format_time_default():
    formatter = MillisecondFormatter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname=__file__, lineno=1,
        msg="msg", args=(), exc_info=None
    )
    record.created = time.time()
    record.msecs = int((record.created - int(record.created)) * 1000)
    formatted_time = formatter.formatTime(record)
    assert isinstance(formatted_time, str)

def test_utc_timezone_formatter_tz_and_converter():
    formatter = UtcTimezoneFormatter(fmt="%(asctime)s", datefmt="%Y-%m-%dT%H:%M:%S.%f%z")
    assert formatter.tz_str == "Z"
    assert formatter.converter == time.gmtime

def test_utc_timezone_formatter_format_time_utc():
    formatter = UtcTimezoneFormatter(fmt="%(asctime)s", datefmt="%Y-%m-%dT%H:%M:%S.%f%z")
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname=__file__, lineno=1,
        msg="msg", args=(), exc_info=None
    )
    record.created = time.time()
    record.msecs = int((record.created - int(record.created)) * 1000)
    formatted_time = formatter.formatTime(record, formatter.datefmt)
    assert formatted_time.endswith("Z")
    assert "." in formatted_time