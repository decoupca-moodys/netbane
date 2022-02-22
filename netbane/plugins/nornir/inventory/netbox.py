import copy

# TODO: remove this dependency
from netdev.netbox import nb
from nornir.core.inventory import Host

REGION_MAP = {}
sites = nb.dcim.sites.filter()
for site in sites:
    if site.region:
        REGION_MAP[site.name] = site.region.slug
    else:
        REGION_MAP[site.name] = None


def get_site_region(site):
    return REGION_MAP[site]


def netbox_transform(host: Host) -> None:
    # store raw netbox data in separate key in case we want it later
    host.data["netbox"] = copy.deepcopy(host.data)
    netbox = host.data["netbox"]
    host.data["site"] = netbox["site"]["slug"].lower()

    # make tags a flat list of slugs
    host.data["tags"] = []
    for tag in netbox["tags"]:
        host.data["tags"].append(tag["slug"])

    # add region
    host.data["region"] = get_site_region(netbox["site"]["name"])
