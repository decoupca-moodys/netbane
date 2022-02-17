from netbane import NetBane
from netdev import config
from pprint import pprint

nxos_host = '172.18.1.19'
ios_host = '172.18.1.4'

netbane_args = {
    'host': nxos_host,
    'username': config.NETWORK_USERNAME,
    'password': config.NETWORK_PASSWORD,
    'platform': 'nxos',
    'optional_args': {
        'ssh_config_file': '~/.ssh/config',
        'default_timeout': 60,
    }
}

device = NetBane(**netbane_args)
device.open()
pprint(device.get_interface_facts())
device.close()

