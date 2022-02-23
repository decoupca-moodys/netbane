from netbane.drivers.cisco.generic import CiscoDriver
from netbane.utils import listify
from netbane.utils.cisco.generic import parse_uptime
from netbane.utils.cisco.ios import int_time


class IOSDriver(CiscoDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       self.SOURCES = {
            "system_facts": [
                {
                    "source": "cmd",
                    "cmd": "show version",
                    "parser": "textfsm",
                    "templates": [
                        'ntc_templates',
                    ],
                },
                {
                    "source": "cmd",
                    "cmd": "show boot",
                    "parser": "textfsm",
                    "templates": [
                        "ntc_templates",
                    ],
                },
            ],
            "interface_facts": [
                {
                    "source": "cmd",
                    "cmd": "show interfaces",
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
        shver = self.parsed["textfsm"]["show_version"]
        shboot = self.parsed["textfsm"]["show_boot"]
        self.system_facts = {
            "code_version": shver["version"],
            "hardware": listify(shver["hardware"]),
            "hostname": shver["hostname"],
            "reload_reason": shver["reload_reason"],
            "running_image": shver["running_image"],
            "serial": listify(shver["serial"]),
            "uptime": shver["uptime"],
            "uptime_sec": parse_uptime(shver["uptime"]),
        }

    def _extract_interface_facts(self):
        pass

    def _normalize_live_interface_facts(self, interface_name):
        """Extracts the facts we need for a given interface from live facts"""
        interface = self._get_live_interface_facts(interface_name)
        return {
            "description": interface["description"],
            "interface": interface["interface"],
            "is_enabled": "disabled" not in interface["protocol_status"],
            "is_up": interface["link_status"].lower() == "up",
            "last_used_sec": int_time(interface["last_output"]),
            "last_used": interface["last_output"],
            "mac": interface["address"],
            "mtu": int(interface["mtu"]),
        }
