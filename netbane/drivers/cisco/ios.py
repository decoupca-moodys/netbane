from netbane.drivers.cisco.generic import CiscoDriver
from netbane.utils.cisco.ios import int_time, parse_uptime

class IOSDriver(CiscoDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.LIVE_INTERFACE_FACTS_CMD = "show interfaces"

    def _normalize_system_facts(self):
        facts = self.parsed["system_facts"]
        return {
            "uptime": facts["uptime"],
            "uptime_sec": parse_uptime(facts["uptime"]),
            "image": facts["running_image"],
        }

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
