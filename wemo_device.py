#!/usr/bin/env python3
"""  Class representing a Belkin Wemo smart device. """

import copy
import json
import re
import string
import sys
from typing import Any, Dict, List
from urllib import parse, request
from xml.etree import ElementTree


STATE_ON = "ON"
STATE_OFF = "OFF"
STATE_UNKNOWN = "UNKNOWN"

REQUEST_TIMEOUT = 5
DEVICE_NODE_TAG = "device"
SERVICE_LIST_NODE_TAG = "serviceList"
SERVICES_TAG = "services"

DATA_DICT_NAME_KEY = "friendlyName"
DEVICE_UNKNOWN = "Unknown Device"
ACTION_GET = '"urn:Belkin:service:basicevent:1#GetBinaryState"'
ACTION_SET = '"urn:Belkin:service:basicevent:1#SetBinaryState"'

REQUEST_HEADERS = {"Content-Type": 'text/xml; charset="utf-8"',
                   "User-Agent": "gecko-home-cli/1.0",
                  }
CONTROL_URI_PATH = "upnp/control/basicevent1"

GET_BINARY_STATE_SOAP_REQUEST = """
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
     soap:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <soap:Body>
        <wemo:GetBinaryState xmlns:wemo="urn:Belkin:service:basicevent:1">
        </wemo:GetBinaryState>
    </soap:Body>
</soap:Envelope>
"""

SET_BINARY_STATE_SOAP_REQUEST_TEMPLATE = string.Template(("""
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
     soap:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <soap:Body>
        <wemo:SetBinaryState xmlns:wemo="urn:Belkin:service:basicevent:1">
            <BinaryState>${STATE}</BinaryState>
        </wemo:SetBinaryState>
    </soap:Body>
</soap:Envelope>
"""))

RESPONSE_BODY_PATH = "{http://schemas.xmlsoap.org/soap/envelope/}Body"
WEMO_GET_STATE_PATH = "{urn:Belkin:service:basicevent:1}GetBinaryStateResponse"
WEMO_SET_STATE_PATH = "{urn:Belkin:service:basicevent:1}SetBinaryStateResponse"


def _log(msg: str, debug: bool = False) -> None:
    """ Logs a message if debugging is turned on. """
    if debug:
        print(f"DEBUG: {msg}")


def _parse_xml(data: str, debug: bool = False) -> ElementTree.Element:
    """ Parse XML document and return the root. """
    try:
        return ElementTree.fromstring(data)

    except ElementTree.ParseError as perr:
        _log(f"XML parse error: {perr}", debug)

    except TimeoutError as zerr:
        _log(f"Request timed out: {zerr}", debug)

    return None


def _get_device_xml(uri: str, timeout: int = REQUEST_TIMEOUT,
                    debug: bool = False) -> ElementTree.Element:
    """ Get device xml (setup.xml) from the specified uri. """
    _log(f"Sending request to {uri} ...")
    info_request = request.Request(url=uri, method="GET")
    with request.urlopen(info_request, timeout=timeout) as zreq:
        _log(f"Location: {uri} -> {zreq.status} {zreq.reason}", debug)
        return _parse_xml(zreq.read())


def _tag(element: ElementTree.Element) -> str:
    """ Returns an element tag without namespace information. """
    return re.sub(r'\{.*?\}', "", element.tag)


def _get_service_info(subtree: ElementTree.Element) -> List[object]:
    """ Get device service information. """
    data = {}
    for node in subtree:
        name = _tag(node)
        data[name] = node.text

    return data


def _get_device_info(device: ElementTree.Element) -> Dict[str, Any]:
    """ Get device information. """
    info = {}
    for node in device:
        name = _tag(node)
        if name == SERVICE_LIST_NODE_TAG:
            info[SERVICES_TAG] = [_get_service_info(svc) for svc in node]
        else:
            info[name] = node.text

    return info


def _wemo_soap_request(uri: str, action: str, data: str,
                       debug: bool = False) -> ElementTree.Element:
    """ Send a soap request to a wemo device. """
    headers = copy.deepcopy(REQUEST_HEADERS)
    headers["SOAPACTION"] = action

    _log(f"Sending wemo soap request to {uri} ...")
    soap_request = request.Request(uri, headers=headers, method="POST",
                                   data=data.encode("utf-8"))

    with request.urlopen(soap_request, timeout=REQUEST_TIMEOUT) as zreq:
        _log(f"Request: {uri} -> {zreq.status} {zreq.reason}", debug)
        data = zreq.read()

        _log(f"Response: {data}", debug)
        return _parse_xml(data)


def _get_device_state(uri: str, debug: bool = False) -> str:
    """ Build and send a soap request to get a device's binary state. """
    data = GET_BINARY_STATE_SOAP_REQUEST
    _log("Sending soap request to get device state ...", debug)
    root = _wemo_soap_request(uri, ACTION_GET, data, debug)
    if root is None:
        _log("invalid soap response", debug)
        return None

    bsxpath = f"{RESPONSE_BODY_PATH}/{WEMO_GET_STATE_PATH}/BinaryState"
    element = root.find(bsxpath)
    if element is not None:
        _log(f"BinaryState {bsxpath} = {element.text}", debug)
        return element.text

    _log(f"Could not find xpath {bsxpath} in xml {root}", debug)
    return None


def _set_device_state(uri: str, state: bool, debug: bool = False) -> str:
    """ Build and send a soap request to set a switch's binary state. """
    params = {"STATE": 1 if state else 0}
    data = SET_BINARY_STATE_SOAP_REQUEST_TEMPLATE.safe_substitute(params)
    _log(f"Sending soap request to set device to {state} ...", debug)

    root = _wemo_soap_request(uri, ACTION_SET, data, debug)
    if root is None:
        _log("invalid soap response", debug)
        return None

    bsxpath = f"{RESPONSE_BODY_PATH}/{WEMO_SET_STATE_PATH}/BinaryState"
    element = root.find(bsxpath)
    if element is not None:
        _log(f"BinaryState {bsxpath} = {element.text}", debug)
        return element.text

    _log(f"Could not find xpath {bsxpath} in xml {root}", debug)
    return None


class WemoDevice:
    """ A Belkin Wemo smart device. """

    def __init__(self, addr: str, yuri: str, debug: bool = False):
        """ Initialize WemoDevice. """
        self._address = addr
        self._uri = yuri
        self._debug = debug
        self._data = {}

        earl = parse.urlparse(yuri)
        base_uri = f"{earl.scheme}://{earl.hostname}:{earl.port}"
        self._control_uri = f"{base_uri}/{CONTROL_URI_PATH}"

        self._load()


    def address(self) -> str:
        """ Endpoint for this device. """
        return self._address


    def name(self) -> str:
        """ Friendly name for this device. """
        return self._data.get(DATA_DICT_NAME_KEY, DEVICE_UNKNOWN)


    def state(self) -> str:
        """ State of the device. """
        zstate = None

        try:
            zstate = _get_device_state(self._control_uri, debug=self._debug)

        #pylint: disable=W0718
        except Exception:
            zstate = None

        if zstate is not None:
            if zstate == "1":
                return STATE_ON

            if zstate == "0":
                return STATE_OFF

        return STATE_UNKNOWN


    def on(self) -> str:
        """ Switch on the device. """
        name = self.name()
        self._log(f"Turning on WemoDevice '{name}' ...")

        zstate = _set_device_state(self._control_uri, 1, debug=self._debug)
        self._log(f"WemoDevice '{name}' state = {zstate}")
        return zstate


    def off(self) -> str:
        """ Switch off the device. """
        name = self.name()
        self._log(f"Turning off WemoDevice '{name}' ...")

        zstate = _set_device_state(self._control_uri, 0, debug=self._debug)
        self._log(f"WemoDevice '{name}' state = {zstate}")
        return zstate


    def asdict(self) -> Dict[str, Any]:
        """ Return dictionary representation of a device. """
        info = {"state": self.state(), "version": "0.0.7"}
        info.update(copy.deepcopy(self._data))
        return info


    def _log(self, msg) -> None:
        """ Logs a debug message if debugging is turned on. """
        _log(msg, self._debug)


    def _load(self) -> None:
        """ Populates Wemo smart device information. """
        root = _get_device_xml(self._uri, debug=self._debug)
        if root is None:
            self._log(f"Error loading info from {self._uri}")
            return

        for node in root:
            name = _tag(node)
            if name == DEVICE_NODE_TAG:
                self._data = _get_device_info(node)


def _dump_wemo_device_info() -> None:
    """ Dump device xml information. """
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]}  <wemo-device-uri>")
        return

    debug_flag = False
    if len(sys.argv) >= 3:
        debug_flag = True

    yuri = sys.argv[1]
    earl = parse.urlparse(yuri)
    device = WemoDevice(addr=earl.hostname, yuri=yuri, debug=debug_flag)

    print(f"cli-test: Device name = {device.name()}")
    print(f"cli-test: address = {device.address()}")
    print(f"cli-test: state = {device.state()}")
    data = json.dumps(device.asdict(), indent=4)
    print(f"cli-test: {data}")


#
#  main():
#
#
if __name__ == "__main__":
    _dump_wemo_device_info()
