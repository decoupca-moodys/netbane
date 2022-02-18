import copy
import re

from scrapli import Scrapli
from ciscoconfparse import CiscoConfParse
from netbane import spec

SCRAPLI_PLATFORM_MAP = {
    "eos": "arista_eos",
    "ios": "cisco_iosxe",
    "iosxr": "cisco_iosxr",
    "nxos": "cisco_nxos",
    "junos": "juniper_junos",
}

# Args to pass to CiscoConfParse
CISCOCONFPARSE_MAP = {
    "ios": {"syntax": "ios", "comment": "!"},
    "nxos": {"syntax": "ios", "comment": "!"},
    "junos": {"syntax": "junos", "comment": "#!"},
}


class BaseDriver(object):
    def __init__(self, host, username, password, platform, optional_args):

        self.host = host
        self.username = username
        self.platform = platform
        self.optional_args = optional_args
        self.ssh_config_file = optional_args.get("ssh_config_file", None)
        self.auth_strict_key = optional_args.get("auth_strict_key", False)
        self.port = optional_args.get("port", 22)
        self.default_timeout = optional_args.get("default_timeout", 30)
        self.timeout_ops = optional_args.get("timeout_ops", self.default_timeout)
        self.timeout_socket = optional_args.get("timeout_socket", self.default_timeout)
        self.timeout_transport = optional_args.get(
            "timeout_transport", self.default_timeout
        )

        scrapli_args = {
            "host": self.host,
            "auth_username": self.username,
            "auth_password": password,
            "auth_strict_key": self.auth_strict_key,
            "platform": SCRAPLI_PLATFORM_MAP[self.platform],
            "port": self.port,
            "ssh_config_file": self.ssh_config_file,
            "timeout_ops": self.timeout_ops,
            "timeout_socket": self.timeout_socket,
            "timeout_transport": self.timeout_transport,
        }
        self.conn = Scrapli(**scrapli_args)

        # completely unformatted facts discovered from device
        # untouched response strings from command output
        self.raw = {
            "running_config": None,
        }

        # facts parsed into a data structure or object, but not yet normalized
        # to conform with spec standard
        self.parsed = {
            # running config as parsed by a library like CiscoConfParse
            "running_config": None,
            # textfsm-parsed interface facts derived from
            # a command like `show interfaces`
            "live_interface_facts": None,
            # interface facts derived from config parsing
            "config_interface_facts": None,
            # textfsm-parsed vlan facts derived from a command like `show vlan`
            "vlans": None,
            # textfsm-parsed system facts derived from a command like `show version`
            "system_facts": None,
        }

        # facts normalized to conform with spec standard
        self.normalized = {
            "live_interface_facts": None,
            "config_interface_facts": None,
            "all_interface_facts": None,
            "system_facts": None,
        }

        # facts ready for use, normalized and collated
        self.interface_facts = None
        self.vlans = None
        self.system_facts = None
        self.LIVE_INTERFACE_NAME_KEY = ""
        self.LIVE_INTERFACE_FACTS_CMD = ""
        self.GET_RUNNING_CONFIG_CMD = ""
        self.GET_SYSTEM_FACTS_CMD = ""

    def open(self):
        self.conn.open()

    def close(self):
        self.conn.close()

    def cli(self, command):
        return self.conn.send_command(command)

    def parse_cli(self, command):
        return self.conn.send_command(command).textfsm_parse_output()

    def _interface_config_regex(self, interface_config, pattern):
        for line in interface_config:
            match = re.match(pattern, line.strip())
            if match:
                return match

    def _fetch_all_live_interface_facts(self):
        """Fetch textfsm-parsed interface facts"""
        self.parsed["live_interface_facts"] = self.parse_cli(
            self.LIVE_INTERFACE_FACTS_CMD
        )

    def _get_live_interface_facts(self, interface_name):
        """Get live facts for a given interface_name"""
        for live_facts in self.parsed["live_interface_facts"]:
            if live_facts[self.LIVE_INTERFACE_NAME_KEY] == interface_name:
                return live_facts

    def _fetch_running_config(self):
        """Fetch raw running config from device"""
        self.raw["running_config"] = self.cli(self.GET_RUNNING_CONFIG_CMD).result

    def _parse_running_config(self):
        if self.raw["running_config"] is None:
            self._fetch_running_config()
        self.parsed["running_config"] = CiscoConfParse(
            self.raw["running_config"].splitlines(), **CISCOCONFPARSE_MAP[self.platform]
        )

    def _fetch_system_facts(self):
        """Fetch textfsm-parsed system facts"""
        self.parsed["system_facts"] = self.parse_cli(self.GET_SYSTEM_FACTS_CMD)[0]

    def _fetch_vlans(self):
        """Fetch textfsm-parsed vlan facts"""
        self.parsed['vlans'] = self.parse_cli(self.GET_VLANS_CMD)

    def _collate_system_facts(self):
        system_facts = copy.deepcopy(spec.SYSTEM_FACTS)
        system_facts.update(self._normalize_system_facts())
        self.normalized["system_facts"] = system_facts

    def _normalize_all_interface_facts(self):
        """Normalizes interface facts from config and live system"""
        live_facts = []
        config_facts = []
        all_facts = []
        for interface in self.parsed["live_interface_facts"]:
            interface_name = interface[self.LIVE_INTERFACE_NAME_KEY]
            combined_facts = copy.deepcopy(spec.INTERFACE_FACTS)
            live_interface_facts = self._normalize_live_interface_facts(interface_name)
            if live_interface_facts:
                live_facts.append(live_interface_facts)
                combined_facts.update(live_interface_facts)
            config_interface_facts = self._normalize_config_interface_facts(
                interface_name
            )
            if config_interface_facts:
                config_facts.append(config_interface_facts)
                combined_facts.update(config_interface_facts)
            all_facts.append(combined_facts)
        self.normalized["live_interface_facts"] = live_facts
        self.normalized["config_interface_facts"] = config_facts
        self.normalized["all_interface_facts"] = all_facts

    def get_system_facts(self):
        if self.system_facts is None:
            self._fetch_system_facts()
            self._normalize_system_facts()
            self._collate_system_facts()
            self.system_facts = self.normalized["system_facts"]
        return self.system_facts

    def get_interface_facts(self):
        if self.interface_facts is None:
            self._fetch_running_config()
            self._fetch_all_live_interface_facts()
            self._normalize_all_interface_facts()
            # self._collate_all_interface_facts()
            self.interface_facts = self.normalized["all_interface_facts"]
        return self.interface_facts

    def get_vlans(self):
        if self.vlans is None:
            self._fetch_vlans()
            self.vlans = self.parsed['vlans']
        return self.vlans
