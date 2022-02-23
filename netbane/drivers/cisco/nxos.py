from netbane.drivers.cisco.generic import CiscoDriver
from netbane.utils import listify
from netbane.utils.cisco.generic import parse_uptime


class NXOSDriver(CiscoDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.LIVE_INTERFACE_FACTS_CMD = "show interface"
        self.SOURCES = {
            "system_facts": [
                {
                    #"source": "cmd",
                    "cmd": "show version",
                    #"parser": "textfsm",
                    #"templates": [
                    #    'ntc_templates',
                    #],
                },
                {
                    #"source": "cmd",
                    "cmd": "show boot",
                    #"parser": "textfsm",
                    #"templates": [
                    #    "ntc_templates",
                    #],
                },
            ],
            "interface_facts": [
                {
                    "source": "cmd",
                    "cmd": "show interface",
                    "parser": "textfsm",
                    'templates': [
                        'ntc_templates',
                    ],
                },
                {
                    "source": "running_config",
                    "cmd": "show running-config",
                    "parser": "ciscoconfparse",
                    'templates': None,
                },
            ],
            "vlans": [
                {
                    "source": "cmd",
                    "cmd": "show vlan",
                    "parser": "textfsm",
                    'templates': [
                        'ntc_templates',
                    ],
                },
            ],
        }

    def _extract_system_facts(self):
        shver = self.parsed['textfsm']["show_version"]
        self.system_facts = {
            "uptime": shver["uptime"],
            "uptime_sec": parse_uptime(shver["uptime"]),
            "running_image": shver["boot_image"],
            "code_version": shver["os"],
            "serial": listify(shver["serial"]),
            "reload_reason": shver["last_reboot_reason"],
            "hardware": listify(shver["platform"]),
        }

    def _normalize_live_interface_facts(self, interface_name):
        interface = self._get_live_interface_facts(interface_name)
        return {
            "description": interface["description"],
            "interface": interface["interface"],
            "is_enabled": interface["admin_state"].lower() == "up",
            "is_up": interface["link_status"].lower() == "up",
            "mac": interface["address"],
            # "mode": interface["mode"], # get this from config facts
            "mtu": int(interface["mtu"]),
        }
