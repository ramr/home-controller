#!/usr/bin/env python3
""" Command line interface to control Belkin Wemo smart devices. """

import argparse
import json
from pathlib import Path
from typing import Dict, List

from discover import discover
from wemo_device import DEVICE_UNKNOWN, WemoDevice
import icons


REGISTRY_JSON = Path(__file__).parent.joinpath("config", "registry.json")

LIST_COMMAND = "list"
INFO_COMMAND = "info"

DISCOVER_COMMANDS = ["discover", "scan", "update"]

ENABLE_COMMANDS = ["on", "enable"]
DISABLE_COMMANDS = ["off", "disable"]
CONTROL_COMMANDS = ENABLE_COMMANDS + DISABLE_COMMANDS

COMMANDS = [LIST_COMMAND, INFO_COMMAND] + DISCOVER_COMMANDS + \
           CONTROL_COMMANDS

ALEXA_IP = "192.168.1.173"
ALEXA = "Alexa"

HEADER_ROW = ["State", "Name", "Host/IP Address", "Status"]
HEADER_DELIMITER_ROW = ['-'*6, '-'*32, '-'*16, '-'*6]
DISPLAY_FORMAT_ROW = "{:<7}  {:<32}  {:<16}  {:<6}"


def _parse_args() -> argparse.Namespace:
    """ Parse command line arguments. """
    commands = ", ".join(COMMANDS)
    parser = argparse.ArgumentParser("Belkin Wemo command line interface")
    parser.add_argument("-s", "--scan", "--discover", required=False,
                        dest="scan", action="store_true",
                        help="Scan for or discover devices")

    #parser.add_argument("-g", "--group", required=False, default="",
    #                    type=str, dest="group", help="Device group")

    parser.add_argument("-d", "--device", required=False, default="",
                        type=str, dest="device", help="Device name")

    parser.add_argument("-c", "--command", default="list", type=str,
                        dest="command", help="One of: " + commands)
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


def _get_device_name(device: WemoDevice) -> str:
    """ Returns device name. """
    name = device.name()
    if name == DEVICE_UNKNOWN and device.address() == ALEXA_IP:
        name = ALEXA

    return name


def _load_registered_devices() -> Dict[str, WemoDevice]:
    """ Load Belkin Wemo devices from local registry. """
    devices = {}
    for data in _load_registry():
        address = data.get("host", "unknown")
        yuri = data["uri"]
        wemo = WemoDevice(address, yuri)

        name = _get_device_name(wemo)
        tag = _tag(name)
        devices[tag] = wemo

    return devices


def _get_registered_devices() -> Dict[str, WemoDevice]:
    """ Get all registered devices in the network. """
    try:
        return _load_registered_devices()

    #pylint: disable=W0718
    except Exception:
        print("ERROR: Loading registered devices, updating registry ...")
        _update_registry()

    return _load_registered_devices()


def _print_device_info(device: WemoDevice, details: bool = False) -> None:
    """ Print info about a specific device. """
    name = _get_device_name(device)
    address = device.address()

    state = device.state() or "?"
    icon = icons.get(state)

    if name == DEVICE_UNKNOWN:
        icon = icons.get(name)

    row = ["", name, address, state]
    fmt_row = "{:<4}  {:<32}  {:<16}  {:<6}"
    print(" ", icon, fmt_row.format(*row))

    if details:
        data = json.dumps(device.asdict(), indent=4)
        print(f"\nDetails:\n{data}")


def _list_registered_devices() -> None:
    """ List out registered devices. """
    devices = _get_registered_devices()
    print("#", DISPLAY_FORMAT_ROW.format(*HEADER_ROW))
    print("#", DISPLAY_FORMAT_ROW.format(*HEADER_DELIMITER_ROW))

    for tag in list(devices.keys()):
        _print_device_info(devices[tag])


def _cli() -> None:
    """ Command line interface for Belkin Wemo smart devices. """
    zargs = _parse_args()
    command = zargs.command
    names = _get_device_names(zargs)

    if zargs.scan or command in DISCOVER_COMMANDS:
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
            print(f"  - Wemo '{wemo.name()}' state = {state}")
            _print_device_info(wemo)
        elif command in DISABLE_COMMANDS:
            state = wemo.off()
            print(f"  - Wemo '{wemo.name()}' state = {state}")
            _print_device_info(wemo)
        elif command in [INFO_COMMAND]:
            _print_device_info(wemo, details=True)


#
#  main():
#
#
if __name__ == "__main__":
    _cli()
