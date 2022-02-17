from netbane.plugins.nornir.connections import NetBane
from netbane.plugins.nornir.inventory.netbox import netbox_transform
from netbane.plugins.nornir.tasks.netbane_get import netbane_get
from nornir import InitNornir
from nornir.core.plugins.connections import ConnectionPluginRegister
from nornir.core.plugins.inventory import TransformFunctionRegister
from nornir_utils.plugins.functions import print_result

TransformFunctionRegister.register("netbox_transform", netbox_transform)
ConnectionPluginRegister.register("netbane", NetBane)

nr = InitNornir(config_file="config.yaml")
host = nr.filter(name="SWTC21AC02")

result = host.run(task=netbane_get, getters=["system_facts"])
print_result(result)
