from ttp import ttp
from rich.pretty import pprint

config_file = '../../ansible/config_backups/FGR/RFGR02CR01.cfg'
template_file = '../templates/ttp/cisco/ios/show_running-config.ttp'

with open(config_file) as fh:
    data  = fh.read()

with open(template_file) as fh:
    template = fh.read()

parser = ttp(data, template)
parser.parse()
pprint(parser.result())
