#!/usr/bin/env python3
""" Discovery devices in a network using SSDP. """

import json
import re
import socket
import sys
from typing import Any, Dict, List


DOOMSDAY = True
READ_BUFFER_SIZE = 32767

SSDP_DISCOVERY_TIMEOUT = 5

#  SSDP multicast address and port.
SSDP_DISCOVERY_ADDRESS = "239.255.255.250"
SSDP_DISCOVERY_PORT = 1900

DISCOVERY_MESSAGE = ["M-SEARCH * HTTP/1.1",
                    f"HOST: {SSDP_DISCOVERY_ADDRESS}:{SSDP_DISCOVERY_PORT}",
                     "ST: upnp:rootdevice",
                     "MX: 3",
                     'MAN: "ssdp:discover"',
                     "",
                     "",
                    ]


def _log(msg: str, debug: bool = False) -> None:
    """ Logs a message if debugging is turned on. """
    if debug:
        print(f"DEBUG: {msg}")


def discover(debug: bool = True) -> List[Dict[str, Any]]:
    """ Discover UPnP devices using SSDP. """
    _log("Starting discovery ...", debug)
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM,
                         proto=socket.IPPROTO_UDP)
    sock.settimeout(SSDP_DISCOVERY_TIMEOUT)

    endpoint = (SSDP_DISCOVERY_ADDRESS, SSDP_DISCOVERY_PORT)
    msg = str.encode("\r\n".join(DISCOVERY_MESSAGE))
    sock.sendto(msg, endpoint)

    devices = []

    try:
        while DOOMSDAY:
            data, addr = sock.recvfrom(READ_BUFFER_SIZE)
            _log(f"Address = {addr}, data = {data}", debug)

            location = ""
            for aline in data.decode("utf-8").split("\r\n"):
                matcher = re.match(r'(?i)Location:\s*', str(aline))
                if matcher:
                    location = str(aline[matcher.end():]).strip()

            info = {"host": addr[0], "uri": location}
            _log(f"Device info = {info}", debug)
            devices.append(info)

    except socket.timeout:
        _log("Discovery complete.", debug)

    return devices


def _print_discovery_info() -> None:
    """ Print discovery info. """
    flag = len(sys.argv) > 1
    devices = discover(debug=flag)
    print(json.dumps(devices, indent=4))


#
#  main():
#
#
if __name__ == "__main__":
    _print_discovery_info()
