from netbane.utils import constants as c
import re


def int_time(int_time):
    # https//github.com/napalm-automation/napalm/blob/develop/napalm/ios/ios.py#L1233
    """
    Convert string time to seconds.
    Examples
    00:14:23
    00:13:40
    00:00:21
    00:00:13
    00:00:49
    1d11h
    1d17h
    1w0d
    8w5d
    1y28w
    never
    """
    int_time = int_time.strip()
    uptime_letters = set(["w", "h", "d"])

    if "never" in int_time:
        return -1
    elif ":" in int_time:
        times = int_time.split(":")
        times = [int(x) for x in times]
        hours, minutes, seconds = times
        return (hours * 3600) + (minutes * 60) + seconds
    # Check if any letters 'w', 'h', 'd' are in the time string
    elif uptime_letters & set(int_time):
        form1 = r"(\d+)d(\d+)h"  # 1d17h
        form2 = r"(\d+)w(\d+)d"  # 8w5d
        form3 = r"(\d+)y(\d+)w"  # 1y28w
        match = re.search(form1, int_time)
        if match:
            days = int(match.group(1))
            hours = int(match.group(2))
            return (days * c.DAY_SECONDS) + (hours * 3600)
        match = re.search(form2, int_time)
        if match:
            weeks = int(match.group(1))
            days = int(match.group(2))
            return (weeks * c.WEEK_SECONDS) + (days * c.DAY_SECONDS)
        match = re.search(form3, int_time)
        if match:
            years = int(match.group(1))
            weeks = int(match.group(2))
            return (years * c.YEAR_SECONDS) + (weeks * c.WEEK_SECONDS)
    raise ValueError(
        "Unexpected value for interface uptime string: {}".format(int_time)
    )
