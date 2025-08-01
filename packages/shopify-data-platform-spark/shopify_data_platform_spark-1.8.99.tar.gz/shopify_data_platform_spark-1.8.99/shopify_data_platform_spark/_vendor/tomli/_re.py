# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 Taneli Hukkinen
# Licensed to PSF under a Contributor Agreement.

import datetime
import re
from typing import Union
from ._types import ParseFloat

# E.g. 07:32:00 or 07:32:00.999999
_TIME_RE_STR = r"([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(?:\.([0-9]{1,6}))?"

RE_NUMBER = re.compile(
    r"""
0
(?:
    x[0-9A-Fa-f](?:_?[0-9A-Fa-f])*   # hex
    |
    b[01](?:_?[01])*                 # bin
    |
    o[0-7](?:_?[0-7])*               # oct
)
|
[+-]?(?:0|[1-9](?:_?[0-9])*)         # dec, integer part
(?P<floatpart>
    (?:\.[0-9](?:_?[0-9])*)?         # optional fractional part
    (?:[eE][+-]?[0-9](?:_?[0-9])*)?  # optional exponent part
)
""",
    re.VERBOSE,
)
RE_LOCALTIME = re.compile(_TIME_RE_STR)
RE_DATETIME = re.compile(
    rf"""
([0-9]{{4}})-([0-9]{{2}})-([0-9]{{2}})  # date part
(?:
    [T ]
    {_TIME_RE_STR}                     # time part
    (?:([zZ])|([+-])([01][0-9]|2[0-3]):([0-5][0-9]))  # optional timezone offset
)?
""",
    re.VERBOSE,
)


def match_to_datetime(match: re.Match) -> datetime.datetime:
    """Convert a `RE_DATETIME` match to `datetime.datetime`."""
    (
        year_str,
        month_str,
        day_str,
        hour_str,
        minute_str,
        sec_str,
        micros_str,
        zulu_time,
        offset_sign_str,
        offset_hour_str,
        offset_minute_str,
    ) = match.groups()
    year, month, day = int(year_str), int(month_str), int(day_str)
    if hour_str is None:
        return datetime.datetime(year, month, day)
    hour, minute, sec = int(hour_str), int(minute_str), int(sec_str)
    micros = int(micros_str.ljust(6, "0")) if micros_str else 0
    if offset_sign_str:
        tz: Union[datetime.timezone, None] = cached_tz(
            offset_hour_str, offset_minute_str, offset_sign_str
        )
    elif zulu_time:
        tz = datetime.timezone.utc
    else:
        tz = None
    return datetime.datetime(year, month, day, hour, minute, sec, micros, tzinfo=tz)


def match_to_localtime(match: re.Match) -> datetime.time:
    hour_str, minute_str, sec_str, micros_str = match.groups()
    hour, minute, sec = int(hour_str), int(minute_str), int(sec_str)
    micros = int(micros_str.ljust(6, "0")) if micros_str else 0
    return datetime.time(hour, minute, sec, micros)


def match_to_number(match: re.Match, parse_float: "ParseFloat") -> Union[int, float]:
    if match.group("floatpart"):
        return parse_float(match.group())
    return int(match.group(), 0)


def cached_tz(hour_str: str, minute_str: str, sign_str: str) -> datetime.timezone:
    sign = 1 if sign_str == "+" else -1
    return datetime.timezone(
        datetime.timedelta(
            hours=sign * int(hour_str),
            minutes=sign * int(minute_str),
        )
    )
