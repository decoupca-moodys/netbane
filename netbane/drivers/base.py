import copy
import re

from scrapli.helper import textfsm_parse
from ciscoconfparse import CiscoConfParse
from scrapli import Scrapli

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

        self._init_sources()

        # completely unformatted facts discovered from device
        # untouched response strings from command output
        self.raw = {
            "running_config": None,
        }

        # facts parsed into a data structure or object, but not yet normalized
        # to conform with spec standard
        self.parsed = {
            "textfsm": {},
            "ttp": {},
            "genie": {},
        }

        # facts ready for use, normalized and collated
        self.interface_facts = None
        self.vlans = None
        self.system_facts = None

    def open(self):
        self.conn.open()

    def close(self):
        self.conn.close()

    def cli(self, command):
        return self.conn.send_command(command)

    def parse_cli(self, command, parser="textfsm", template=None):
        response = self.conn.send_command(command)
        if parser == "textfsm":
            if template is None or template == "ntc_templates":
                return response.textfsm_parse_output()
            else:
                return textfsm_parse(template, response.result)
        elif parser == "genie":
            if template is not None:
                raise ValueError("Genie does not support custom templates")
            return response.genie_parse_output()
        elif parser == "ttf":
            return response.ttf_parse_output(template=template)
        else:
            raise ValueError(
                f"Unknown parser: {parser}. Must use textfsm, genie, or ttf."
            )

    def _init_sources(self):
        for getter, sources in self.SOURCES.items():
            for source in sources:
                if not source.get("cmd"):
                    raise ValueError(
                        f'Source definition for {getter} missing required "cmd"'
                    )
                source["source"] = source.get("source", "cmd")
                source["parsers"] = source.get("parsers", [self.DEFAULT_PARSER])

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
        self.parsed["vlans"] = self.parse_cli(self.GET_VLANS_CMD)

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

    def _sanitize_cmd(self, cmd):
        return cmd.replace(" ", "_")

    def _fetch_parser_data(self, cmd, parser):
        if isinstance(parser, str):
            parser_name = parser
            output = self.parse_cli(cmd, parser=parser_name)
        elif isinstance(parser, dict):
            for parser_name, templates in parser.items():
                for template in templates:
                    output = self.parse_cli(cmd, parser=parser_name, template=template)
                    if output:
                        break

        # un-nest single-element lists
        if isinstance(output, list) and len(output) == 1:
             output = output[0]

        return output

    def _fetch(self, getter=None, force=False):
        sources = self.SOURCES[getter]
        for source in sources:
            cmd = source["cmd"]
            parsers = source["parsers"]
            if source["source"] == "running_config":
                local_cache = self.raw
                cache_key = "running_config"
                data = local_cache.get(cache_key)
                if data is None or force:
                    local_cache[cache_key] = self.cli(cmd)
            else:
                for parser in parsers:
                    if isinstance(parser, str):
                        parser_name = parser
                    elif isinstance(parser, dict):
                        parser_name = list(parser.keys())[0]
                    local_cache = self.parsed[parser_name]
                    cache_key = self._sanitize_cmd(cmd)
                    data = local_cache.get(cache_key)
                    if data is None or force:
                        output = self._fetch_parser_data(cmd, parser)
                        local_cache[cache_key] = output

    def _extract(self, getter=None):
        method = getattr(self, f"_extract_{getter}")
        method()

    def get_system_facts(self, force=False):
        self._fetch("system_facts", force=force)
        self._extract("system_facts")
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
            self.vlans = self.parsed["vlans"]
        return self.vlans
