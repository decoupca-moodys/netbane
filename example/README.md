# netbane

A unified, pure Python API to manage all network devices, built on napalm and nornir.

The name is a nod to Isildur's Bane, the One Ring to Rule Them All from Lord of the Rings :)

## Why not just napalm and nornir?

Napalm and nornir are a great start. They even support plugins for custom tasks or unsupported devices.

But say I want to add a simple feature like `get_cdp_neighbors()` for IOS devices. What happens when you want to extend the core functionality of an *existing* napalm driver? Napalm's focus on vendor abstraction doesn't allow proprietary features like CDP, so I can't submit a PR to patch the existing IOS driver. But, surely I don't need to write a custom napalm driver from scratch.

Netbane provides a framework for such cases.

With netbane, you get all the built-in features of napalm, with the ability to extend core features in a straightforward and maintanable way.

Netbane also includes connection and task plugins for nornir to leverage the new features.

## Overview

The goal is to keep things as similar to napalm as possible, while providing a means to extend core functionality.

Netbane provides a custom `get_network_driver()` method that will search for a custom netbane driver, then fall back to a native napalm driver if not found:

```py
from netbane import get_network_driver
from pprint import pprint
driver = get_network_driver('ios')
device = driver(hostname='my_host', username='my_user', password='my_password')
device.open()
cdp_neighbors = device.get_cdp_neighbors()
pprint(cdp_neighbors)
```
