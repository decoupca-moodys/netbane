from netbane.drivers.cisco.base import CiscoDriver
from netbane.utils import listify, dictify
from netbane.utils.cisco.generic import parse_uptime
from netbane.utils.cisco.ios import int_time


class IOSDriver(CiscoDriver):
    def __init__(self, *args, **kwargs):
        self.LIVE_INTERFACE_FACTS_CMD = "show interfaces"
        self.DEFAULT_PARSER = "textfsm"
        self.SOURCES = {
            "system_facts": [
                {
                    "cmd": "show version",
                    "parsers": [
                        # "genie",
                        "textfsm",
                    ],
                },
                {
                    "cmd": "show boot",
                    "parsers": [
                        # "genie",
                        "textfsm",
                    ],
                },
            ],
            "interface_facts": [
                {
                    "cmd": "show interfaces",
                },
                {
                    "source": "running_config",
                    "cmd": "show running-config",
                    "parsers": ["ttp"],
                    "templates": None,
                },
            ],
            "vlans": [
                {
                    "cmd": "show vlan",
                },
            ],
        }

        super().__init__(*args, **kwargs)

    def _get_interface_config(self, interface_name):
        return self.parsed["ttp"]["running_config"]["interfaces"].get(
            interface_name, dict()
        )

    def _get_interface_data(self, interface_name):
        return [
            x
            for x in self.parsed["textfsm"]["show_interfaces"]
            if x["interface"] == interface_name
        ][0]

    def _extract_system_facts(self):
        shver = self.parsed["textfsm"]["show_version"]
        shboot = self.parsed["textfsm"]["show_boot"]
        return {
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
        interface_facts = {}
        shint = self.parsed["textfsm"]["show_interfaces"]
        shint = dictify(shint, old_key="interface", new_key="name")
        for interface_name, data in shint.items():
            cfg = self._get_interface_config(interface_name)
            interface_facts.update(
                {
                    interface_name: {
                        "access_vlan": cfg.get("switchport_access_vlan"),
                        "description": data.get("description")
                        or cfg.get("description"),
                        "name": interface_name,
                        "is_enabled": "disabled" not in data.get("protocol_status"),
                        "is_up": data.get("link_status").lower() == "up",
                        "last_used": data.get("last_output"),
                        "last_used_sec": int_time(data.get("last_output")),
                        "mac": data.get("address"),
                        "mtu": int(data.get("mtu")),
                        "mode": cfg.get("mode") or data.get("mode"),
                    }
                }
            )
        return interface_facts
