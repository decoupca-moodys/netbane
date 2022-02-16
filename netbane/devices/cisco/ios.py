from netbane.devices.cisco.generic import CiscoDevice

class IOSDevice(CiscoDevice):
    def __init__(self, nb_device):
        super().__init__(nb_device)
        self.LIVE_INTERFACE_FACTS_CMD = "show interfaces"

    def _normalize_system_facts(self):
        facts = self.parsed["system_facts"]
        return {
            "uptime": facts["uptime"],
            "uptime_sec": ios.parse_uptime(facts["uptime"]),
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
            "last_used_sec": ios.int_time(interface["last_output"]),
            "last_used": interface["last_output"],
            "mac": interface["address"],
            "mtu": int(interface["mtu"]),
        }
