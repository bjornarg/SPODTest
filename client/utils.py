# -*- coding: utf-8 -*-

import datetime
import time
import re

def date_to_rfc3339(date):
    """ Converts a datetime.datetime object or time.time() to RFC3339 string. 
    
    """
    if isinstance(date, float) or isinstance(date, int):
        date = datetime.datetime.fromtimestamp(date)
    if not isinstance(date, datetime.datetime):
        return False
    date_str = "%Y-%m-%dT%H:%M:%S"
    if date.tzinfo is not None:
        timedelta = (date.dst() or date.utcoffset())
        timedelta = timedelta.days * 86400 + timedelta.seconds
    else:
        it = time.mktime(date.timetuple())
        if time.localtime(it).tm_isdst:
            timedelta = -time.altzone
        else:
            timedelta = -time.timezone
    zone_prefix = "-"
    if timedelta >= 0:
        zone_prefix = "+"
    offset = "%s%02d:%02d" % (zone_prefix, abs(timedelta/3600), abs(timedelta%3600/60))
    return "%s%s" % (date.strftime(date_str), offset)

def rfc3339_to_date(date_str):
    """ Converts a string to datetime.datetime object if string is a valid
    RFC3339 date.

    Returns False for any string that is not valid RFC3339.
    
    """
    rfc3339_match = r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:([+]|[-])(\d{2}):(\d{2})|(Z))$"
    match = re.match(rfc3339_match, date_str.strip())
    if match is None:
        return False
    try:
        dt_obj = datetime.datetime(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            int(match.group(4)),
            int(match.group(5)),
            int(match.group(6)),
            )
    except ValueError:
        # If any values outside allowed range (e.g. month 15), a ValueError
        # is raised by datetime.datetime() and we have an invalid date.
        return False
    if match.group(7) is not None and match.group(8) is not None \
        and match.group(9) is not None:
        if int(match.group(8))*60+int(match.group(9)) >= 1439:
            return False
    if match.group(10) is not None and match.group(10) != "Z":
        return False
        
    return dt_obj
