#!/usr/bin/env python3
""" Command line interface to control Belkin Wemo smart devices. """

import argparse
import json
from pathlib import Path
from typing import Dict, List

from discover import discover
from wemo_device import WemoDevice
from icons import STATE_DOWN_ICON, STATE_UNKNOWN_ICON, STATE_UP_ICON


REGISTRY_JSON = Path(__file__).parent.joinpath("config", "registry.json")

LIST_COMMAND = "list"
UPDATE_COMMANDS = ["update", "scan", "discover"]
ENABLE_COMMANDS = ["on", "enable"]
DISABLE_COMMANDS = ["off", "disable"]
CONTROL_COMMANDS = ENABLE_COMMANDS + DISABLE_COMMANDS
COMMANDS = [LIST_COMMAND] + UPDATE_COMMANDS + CONTROL_COMMANDS


def _parse_args() -> argparse.Namespace:
    """ Parse command line arguments. """
    commands = ", ".join(COMMANDS)
    parser = argparse.ArgumentParser("Belkin Wemo command line interface")
    parser.add_argument("-d", "--device", default="", type=str,
                        dest="device", help="Device name")
    #parser.add_argument("-g", "--group", default="", type=str,
    #                    dest="group", help="Device group")
    parser.add_argument("-c", "--command", default="list", type=str,
                        dest="command",
                        help="One of: " + commands)
    return parser.parse_args()



def _get_device_names(args: argparse.Namespace) -> List[str]:
    """ Return the list of device names to operate on. """
    devices = []

    #if args.group:
    #    devices = _get_devices_in_group(args.group)

    if args.device:
        devices.append(args.device)

    return devices


def _update_registry() -> None:
    """ Update device registry information. """
    data = discover(debug=False)
    with REGISTRY_JSON.open("wt", encoding="utf-8") as json_fp:
        json_fp.write(json.dumps(data, indent=4))


def _load_registry() -> List[object]:
    """ Load device registry. """
    if not REGISTRY_JSON.exists():
        _update_registry()

    with REGISTRY_JSON.open("rt", encoding="utf-8") as json_fp:
        return json.loads(json_fp.read())


def _tag(name: str) -> str:
    """ Convert a device name into a unique tag for searching. """
    tag = name.lower()
    return tag.replace(" ", "-")


def _load_registered_devices() -> Dict[str, WemoDevice]:
    """ Load Belkin Wemo devices from local registry. """
    devices = {}
    for data in _load_registry():
        if "uri" in data:
            wemo = WemoDevice(data["uri"])
            tag = _tag(wemo.name())
            devices[tag] = wemo

    return devices


def _get_icon(state: str) -> object:
    """ Return device icon for state. """
    if state.lower() in ["off", "0"]:
        return STATE_DOWN_ICON

    if state.lower() in ["on", "1"]:
        return STATE_UP_ICON

    return STATE_UNKNOWN_ICON


def _get_registered_devices() -> Dict[str, WemoDevice]:
    """ Get all registered devices in the network. """
    try:
        return _load_registered_devices()

    #pylint: disable=W0718
    except Exception:
        print("ERROR: Loading registered devices, updating registry ...")
        _update_registry()

    return _load_registered_devices()


def _list_registered_devices() -> None:
    """ List out registered devices. """
    devices = _get_registered_devices()
    for tag in list(devices.keys()):
        dev = devices[tag]
        name = dev.name()
        address = dev.address()
        state = dev.state()
        icon = _get_icon(state)
        print(f"{name.ljust(32)} {address.ljust(16)} {state} {icon}")


def _cli() -> None:
    """ Command line interface for Belkin Wemo smart devices. """
    zargs = _parse_args()
    command = zargs.command
    names = _get_device_names(zargs)

    if command in UPDATE_COMMANDS:
        _update_registry()
        _list_registered_devices()
        return

    if command == LIST_COMMAND:
        _list_registered_devices()
        return

    devices = _get_registered_devices()

    if len(names) < 1:
        return

    for k in names:
        tag = _tag(k)
        if tag not in devices:
            print(f"ERROR: No Belkin Wemo device named {k} was found.")
            continue

        wemo = devices[tag]
        if command in ENABLE_COMMANDS:
            state = wemo.on()
            icon = _get_icon(state)
            print(f"  - Wemo {wemo.name()}  state = {state} {icon}")
        elif command in DISABLE_COMMANDS:
            state = wemo.off()
            icon = _get_icon(state)
            print(f"  - Wemo {wemo.name()}  state = {state} {icon}")


#
#  main():
#
#
if __name__ == "__main__":
    _cli()
