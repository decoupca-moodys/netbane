from netbane.drivers.base import BaseDriver


class CiscoDriver(BaseDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.GET_RUNNING_CONFIG_CMD = "show run"
        self.LIVE_INTERFACE_NAME_KEY = "interface"
        self.GET_VLANS_CMD = "show vlan"
        self.GET_SYSTEM_FACTS_CMD = "show version"

    def _get_vlan_name(self, vlan_id):
        if vlan_id is None:
            return None
        if self.vlans is None:
            self._fetch_vlans()
        for vlan in self.vlans:
            if int(vlan['vlan_id']) == vlan_id:
                return vlan['name']
        # I thought it was impossible, but I did encounter an edge
        # case where a port had an access vlan ID assigned that did
        # not show up in the vlan list
        return None

    def _get_interface_config_lines(self, interface_name):
        if self.parsed["running_config"] is None:
            self._parse_running_config()
        return self.parsed["running_config"].find_children(
            f"^interface {interface_name}", exactmatch=True
        )

    def _get_interface_config_object(self, interface_name):
        if self.parsed["running_config"] is None:
            self._parse_running_config()
        config_object = self.parsed["running_config"].find_objects(
            f"^interface {interface_name}", exactmatch=True
        )
        if config_object:
            return config_object[0]
        else:
            return None

    def _get_interface_mode(self, interface_config):
        match = self._interface_config_regex(interface_config, r"^no\sswitchport$")
        if match:
            return "routed"
        pattern = r"^switchport\s+mode\s+(access|trunk)"  # noqa
        match = self._interface_config_regex(interface_config, pattern)
        if match:
            return match.group(1)
        else:
            return "access"

    def _get_interface_vlan(self, vlan_type, interface_config):
        if vlan_type == "native":
            cfg = r"trunk\snative"
        else:
            cfg = vlan_type
        pattern = f"^switchport\s{cfg}\svlan\s(\d+)"  # noqa
        match = self._interface_config_regex(interface_config, pattern)
        if match:
            return int(match.group(1))
        else:
            mode = self._get_interface_mode(interface_config)
            if (mode == "access" and vlan_type == "access") or (
                mode == "trunk" and vlan_type == "native"
            ):
                return 1
            else:
                return None

    def _normalize_config_interface_facts(self, interface_name):
        interface_config = self._get_interface_config_lines(interface_name)
        if interface_config:
            interface_object = self._get_interface_config_object(interface_name)
            return {
                "interface": interface_name,
                "mode": self._get_interface_mode(interface_config),
                "access_vlan": self._get_interface_vlan("access", interface_config),
                "native_vlan": self._get_interface_vlan("native", interface_config),
                "is_ethernet": interface_object.is_ethernet_intf,
            }
        else:
            return None
