from ciscoconfparse import CiscoConfParse

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
        vlan_dict = next(x for x in self.vlans if int(x["vlan_id"]) == vlan_id)
        return vlan_dict["name"]

    # TODO: may be able to move this to BaseClass, since CiscoConfParse can
    # handle configs from many vendors
    def _parse_running_config(self):
        if self.raw["running_config"] is None:
            self._fetch_running_config()
        self.parsed["running_config"] = CiscoConfParse(
            self.raw["running_config"].splitlines()
        )

    def _get_interface_config_lines(self, interface_name):
        if self.parsed["running_config"] is None:
            self._parse_running_config()
        return self.parsed["running_config"].find_children(
            f"^interface {interface_name}", exactmatch=True
        )

    def _get_interface_config_object(self, interface_name):
        if self.parsed["running_config"] is None:
            self._parse_running_config()
        return self.parsed["running_config"].find_objects(
            f"^interface {interface_name}", exactmatch=True
        )[0]

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
        interface_object = self._get_interface_config_object(interface_name)
        return {
            "interface": interface_name,
            "mode": self._get_interface_mode(interface_config),
            "access_vlan": self._get_interface_vlan("access", interface_config),
            "native_vlan": self._get_interface_vlan("native", interface_config),
            "is_ethernet": interface_object.is_ethernet_intf,
        }
