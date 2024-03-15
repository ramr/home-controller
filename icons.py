#!/usr/bin/env python3
""" Icons for state and devices. """

RED_COLOR = "\033[31m"
GREEN_COLOR = "\033[32m"
END_COLOR = "\033[m"

OFF_STATE = "\u25BC "       # alternatives: "\u23FC" or "○"
ON_STATE = "\u23FB "        # alternatives: "◉"
#UNKNOWN_STATE = "\uFFFD"   # alternatives: "?"
UNKNOWN_STATE = "\u26A1"    # alternatives: "?"

UNKNOWN_DEVICE_ICON = "⯑ "


def build(icon: str = "", color: str = None) -> str:
    """ Build icon based on color scheme. """
    if color is not None:
        return f"{color}{icon}{END_COLOR}"

    return icon


def get(name: str, colorize: bool = True) -> object:
    """ Return device icon for name. """
    icon = UNKNOWN_STATE
    color = GREEN_COLOR
    if name.lower() in ["off", "0"]:
        icon = OFF_STATE
        color = RED_COLOR

    if name.lower() in ["on", "1"]:
        icon = ON_STATE
        color = GREEN_COLOR

    if name.lower() in ["unknown", "?"]:
        icon = UNKNOWN_STATE
        color = GREEN_COLOR

    if name.lower() in ["unknown device"]:
        icon = UNKNOWN_DEVICE_ICON
        color = RED_COLOR

    return build(icon, color if colorize else None)
