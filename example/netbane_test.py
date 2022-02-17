from pprint import pprint

from netbane import NetBane
from netdev import config

nxos_host = "172.18.0.5"
ios_host = "172.18.1.4"

netbane_args = {
    "host": ios_host,
    "username": config.NETWORK_USERNAME,
    "password": config.NETWORK_PASSWORD,
    "platform": "ios",
    "optional_args": {
        "ssh_config_file": "~/.ssh/config",
        "default_timeout": 60,
    },
}

device = NetBane(**netbane_args)
device.open()
pprint(device.get_system_facts())
import ipdb

ipdb.set_trace()
device.close()
