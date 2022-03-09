from rich.pretty import pprint
from ttp import ttp

config_file = "test.cfg"
template_file = "../templates/cisco/ios/show_running-config.ttp"

with open(config_file) as fh:
    data = fh.read()

with open(template_file) as fh:
    template = fh.read()

parser = ttp(data, template)
parser.parse()
pprint(parser.result())
