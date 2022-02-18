from netbane.drivers.cisco.ios import IOSDriver
from netbane.drivers.cisco.nxos import NXOSDriver
from netbane.drivers.juniper.junos import JUNOSDriver

DRIVER_MAP = {
    "ios": IOSDriver,
    "nxos": NXOSDriver,
    "junos": JUNOSDriver,
}


class NetBane(object):
    def __new__(self, host, username, password, platform, optional_args):
        return DRIVER_MAP[platform](host, username, password, platform, optional_args)
