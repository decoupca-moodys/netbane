import re

from netbane.utils import constants as c


def parse_uptime(uptime_str):
    """
    Extract the uptime string from the given Cisco device.
    Return the uptime in seconds as an integer
    """
    # Initialize to zero
    (years, weeks, days, hours, minutes, seconds) = (0, 0, 0, 0, 0, 0)

    uptime_str = uptime_str.strip()
    time_list = uptime_str.split(",")
    for element in time_list:
        if re.search("year", element):
            years = int(element.split()[0])
        elif re.search("week", element):
            weeks = int(element.split()[0])
        elif re.search("day", element):
            days = int(element.split()[0])
        elif re.search("hour", element):
            hours = int(element.split()[0])
        elif re.search("minute", element):
            minutes = int(element.split()[0])
        elif re.search("second", element):
            seconds = int(element.split()[0])

    uptime_sec = (
        (years * c.YEAR_SECONDS)
        + (weeks * c.WEEK_SECONDS)
        + (days * c.DAY_SECONDS)
        + (hours * 3600)
        + (minutes * 60)
        + seconds
    )
    return uptime_sec
