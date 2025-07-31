import logging
import time
from typing import Optional

class MillisecondFormatter(logging.Formatter):
    """
    Formatter for Python logging that adds millisecond precision to log timestamps
    and formats the timezone offset as "+HH:MM" or "-HH:MM".

    By default, uses the local timezone and supports custom date/time formats
    with millisecond and timezone placeholders ("%f" for milliseconds, "%z" for offset).
    """
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, style: str = '%') -> None:
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        org_tz = time.strftime('%z')
        if org_tz and len(org_tz) == 5 and (org_tz[0] == '+' or org_tz[0] == '-'):
            self.tz_str = f"{org_tz[0]}{org_tz[1:3]}:{org_tz[3:5]}"
        else:
            self.tz_str = org_tz

    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        ct = self.converter(record.created)
        if datefmt:
            datefmt = datefmt.replace("%f", "%03d" % int(record.msecs))
            datefmt = datefmt.replace('%z', self.tz_str)
            s = time.strftime(datefmt, ct)
        else:
            s = time.strftime(self.default_time_format, ct)
            if self.default_msec_format:
                s = self.default_msec_format % (s, record.msecs)
        return s

class UtcTimezoneFormatter(MillisecondFormatter):
    """
    Formatter for Python logging that outputs log timestamps in UTC (GMT) with millisecond
    precision and a 'Z' suffix to indicate zero offset.

    Inherits from MillisecondFormatter and overrides the timezone to always be UTC.
    """
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, style: str = '%') -> None:
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.tz_str = 'Z'

        # Set the converter to gmtime for UTC
        self.converter = time.gmtime
