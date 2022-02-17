from netbane import NetBane
from netdev import config
from pprint import pprint

netbane_args = {
    'host': '172.18.1.4',
    'username': config.NETWORK_USERNAME,
    'password': config.NETWORK_PASSWORD,
    'platform': 'ios',
    'optional_args': {
        'ssh_config_file': '~/.ssh/config',
        'default_timeout': 60,
    }
}

device = NetBane(**netbane_args)
device.open()
pprint(device.get_interface_facts())
device.close()

