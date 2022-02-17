from nornir.core.inventory import Host
import copy

def netbox_transform(host: Host) -> None:
    # store raw netbox data in separate key in case we want it later
    host.data["netbox"] = copy.deepcopy(host.data)
    netbox = host.data["netbox"]
    host.data["site"] = netbox["site"]["slug"].lower()

    # make tags a flat list of slugs
    host.data['tags'] = []
    for tag in netbox['tags']:
        host.data['tags'].append(tag['slug'])
