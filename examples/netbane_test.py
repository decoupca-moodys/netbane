from netdev import config
from rich.pretty import pprint

from netbane import NetBane

nxos_host = "172.18.0.5"
ios_host = "172.18.58.4"
junos_host = "172.25.22.10"
aireos_host = '10.136.186.11'

netbane_args = {
    "host": aireos_host,
    "username": config.NETWORK_USERNAME,
    "password": config.NETWORK_PASSWORD,
    "platform": "aireos",
    "optional_args": {
        "ssh_config_file": "~/.ssh/config",
        "default_timeout": 60,
    },
}

device = NetBane(**netbane_args)
device.open()
# pprint(device.get_system_facts())
# pprint(device.get_interface_facts())
# device._fetch("interface_facts")
# device._parse("interface_facts")
pprint(device.get_ap_facts())
# pprint(device.parsed['running_config'])
import ipdb

ipdb.set_trace()
device.close()
