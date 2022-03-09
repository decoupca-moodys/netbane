from netbane.drivers.cisco.base import CiscoDriver
from netbane.utils import listify, dictify
from netbane.utils.cisco.generic import parse_uptime
from netbane.utils.cisco.ios import int_time


class AireOSDriver(CiscoDriver):
    def __init__(self, *args, **kwargs):
        self.LIVE_INTERFACE_FACTS_CMD = "show interfaces"
        self.DEFAULT_PARSER = "textfsm"
        self.SOURCES = {
            "ap_facts": [
                {
                    "cmd": "show ap summary",
                },
            ],
            "system_facts": [
                {
                    "cmd": "show system info",
                    "parsers": [
                        # "genie",
                        "textfsm",
                    ],
                },
            ],
        }

        super().__init__(*args, **kwargs)

    def _extract_ap_facts(self):
        sh_ap_summ = self.parsed["textfsm"]["show_ap_summary"]
        return sh_ap_summ

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
