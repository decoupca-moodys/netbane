from netbane.drivers.cisco.generic import CiscoDriver
from netbane.utils import listify
from netbane.utils.cisco.generic import parse_uptime


class NXOSDriver(CiscoDriver):
    def __init__(self, *args, **kwargs):
        self.LIVE_INTERFACE_FACTS_CMD = "show interface"
        self.DEFAULT_PARSER = "textfsm"
        # each key corresponds to the getter name
        # values are a list of sources for that getter
        # each source must include a 'cmd' to run
        # each source may specify one or more parsing engines
        # to parse the 'cmd' with.
        # each of these may have one or more templates to try.
        # For each (getter, parser) combination, netbane will
        # return at most one parsed result.
        self.SOURCES = {
            "system_facts": [
                {
                    # the only required key for each getter is 'cmd'
                    # the 'cmd' will be parsed by DEFAULT_PARSER using
                    # default options for that parser.
                    "cmd": "show version",
                },
                {
                    # if we want to use a different parser or parsing
                    # options, set them like this:
                    "cmd": "show boot",
                    "parsers": [
                        # genie does not support any options,
                        # so we can pass it as a string.
                        "genie",
                        # we can pass textfsm as a string to use
                        # default settings, or as a dict to customize.
                        # the key is the parsing engine, value is
                        # a list of templates to try, stopping at the first
                        # one that works.
                        {
                            "textfsm": [
                                # this will try the default ntc_template for
                                # `show boot`
                                "ntc_templates",
                                # if that doesn't work (returns an empty list),
                                # try this custom template
                                # "templates/textfsm/my_custom_template.textfsm",
                            ]
                        },
                    ],
                },
            ],
            "interface_facts": [
                {
                    "source": "cmd",
                    "cmd": "show interface",
                    "parser": "textfsm",
                    "templates": [
                        "ntc_templates",
                    ],
                },
                {
                    "source": "running_config",
                    "cmd": "show running-config",
                    "parser": "ciscoconfparse",
                    "templates": None,
                },
            ],
            "vlans": [
                {
                    "source": "cmd",
                    "cmd": "show vlan",
                    "parser": "textfsm",
                    "templates": [
                        "ntc_templates",
                    ],
                },
            ],
        }

        super().__init__(*args, **kwargs)

    def _extract_system_facts(self):
        shver = self.parsed["textfsm"]["show_version"]
        self.system_facts = {
            "uptime": shver["uptime"],
            "uptime_sec": parse_uptime(shver["uptime"]),
            "running_image": shver["boot_image"],
            "code_version": shver["os"],
            "serial": listify(shver["serial"]),
            "reload_reason": shver["last_reboot_reason"],
            "hardware": listify(shver["platform"]),
        }

    def _normalize_live_interface_facts(self, interface_name):
        interface = self._get_live_interface_facts(interface_name)
        return {
            "description": interface["description"],
            "interface": interface["interface"],
            "is_enabled": interface["admin_state"].lower() == "up",
            "is_up": interface["link_status"].lower() == "up",
            "mac": interface["address"],
            # "mode": interface["mode"], # get this from config facts
            "mtu": int(interface["mtu"]),
        }
