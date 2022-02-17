from netbane.drivers.cisco.generic import CiscoDriver
from netbane.utils.cisco.generic import parse_uptime
from netbane.utils.cisco.ios import int_time


class IOSDriver(CiscoDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.LIVE_INTERFACE_FACTS_CMD = "show interfaces"

    def _normalize_system_facts(self):
        facts = self.parsed["system_facts"]
        return {
            "code_version": facts["version"],
            "hardware": facts["hardware"],
            "running_image": facts["running_image"],
            "uptime": facts["uptime"],
            "uptime_sec": parse_uptime(facts["uptime"]),
            "hostname": facts["hostname"],
            "reload_reason": facts["reload_reason"],
            "serial": facts["serial"],
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
