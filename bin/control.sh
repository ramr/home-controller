#!/bin/bash

readonly CONTROLLER_CLI="${HOME}/github/home-controller/cli.py"


#
#  Control a device.
#
#  Usage:  _control_device  <name>  on|off
#
#  Examples:
#      _control_device  "LivingRoom Floor Lamp"  on  # or ON
#
#      _control_device  "Hutch Lights"  OFF
#
#      _control_device  hutch-Lights  off
#
function _control_device() {
    local name=${1:-""}
    local state=${2:-""}

    if [ -z "${name}" ] || [ -z "${state}" ]; then
        echo "Usage: $0  <name>  on|off"
        echo "Control a device - turn it on or off."
        echo ""
        echo "Where:"
        echo "     <name> needs to be quoted if a device name has spaces"
        echo "            (example 'Living Room Lights') or you can replace"
        echo "            spaces with a hyphen character (-). The names are"
        echo "            also case-insensitive ... so 'My  Desk Lamp' is"
        echo "            the same as \"my- Desk lamp\" or my--Desk-lamp."
        echo "            Note there are 2 spaces between my and desk."
        echo ""
        echo "Examples: "
        echo "    $0  'LivingRoom Floor Lamp'  on  # or ON"
        echo "    $0  livingroom-floor-lamp  ON  # or ON"
        echo "    $0  \"Hutch Lights\"  OFF"
        echo "    $0  hutch-Lights  off"
        echo ""
        exit 64
    fi

    echo "  - Sending device '${name}' command to turn itself ${state} ..."
    exec "${CONTROLLER_CLI}" -d "${name}" -c "${state}"

}  #  End of function  _control_device.


#
#  _main():
#
_control_device "$@"
