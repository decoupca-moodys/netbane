INTERFACE_FACTS = {
    # (str) full interface name - GigabitEthernet1/0/25
    "interface": None,
    # (str) administratively-defined description, if any
    "description": None,
    # (bool) line/protocol status
    # None if unknown
    "is_up": None,
    # (bool) administrative status
    "is_enabled": None,
    # (bool or none) whether or not the interface is a physical port (not virtual)
    "is_physical": None,
    # (bool) whether or not the interface is virtual (not physical)
    "is_virtual": None,
    # (bool) whether or not the interface is fixed (built-in, not modular)
    "is_fixed": None,
    # (bool) whether or not the interface is modular (SFP, etc. opposite of fixed)
    "is_modular": None,
    # (bool) whether or not the port is for management only
    "is_management": None,
    # (bool) whether or not the port is Ethernet (10M thru 10G)
    "is_ethernet": None,
    # (bool) whether or not the interface is a child interface
    "is_subinterface": None,
    # (dict) primary IPv4 address in CIDR notation, None if not set
    "primary_ip4": None,  # {'address': '', 'prefix_length': 0, 'cidr': '' },
    # (list of dicts or none) list of secondary IPv4 addresses, if any. None if not set.
    "secondary_ip4": None,
    # (str) MAC address of interface, if exists
    "mac": None,
    # (int) MTU of interface
    "mtu": None,
    # (int or None) time in seconds since last traffic passed. -1 if never,
    #               None if unknown
    "last_used_sec": None,
    # (str or None) human-readable time since last passed traffic.
    # -1 if never, None if unknown
    "last_used": None,
    # (str) port mode: access, trunk or routed. empty string if unknown.
    "mode": None,
}


SYSTEM_FACTS = {
    "image": None,
    "uptime": None,
    "uptime_sec": None,
}
