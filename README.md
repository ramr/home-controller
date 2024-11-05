# home-controller

A very basic smart home controller for wemo and tapo `smart` devices.

## Usage

There is a simple control.sh script that allows you to turn `on` and `off`
any discovered device in your network.

The device name should be quoted if it has any spaces or you replace the
spaces with a hypen character (`-`). The names are also case insensitive,
so if your device is named `"My  Desk Lamp"` between `My` and `Desk`)
is the same as `"my- Desk lamp"` or `my--desk-Lamp`.

Note: There are 2 spaces between `My` and `Desk` in `"My  Desk Lamp"`.

```shell
/path/to/this/repo/bin/control.sh  <device-name>  <state>
#  Usage: /path/to/this/repo/bin/control.sh  <device-name>  <state>
#         <device-name> is a quoted device name or hyphenated in lieu of
#                       spaces for a non-quoted name.
#         <state>       is one of: on, off, enable or disable.

#  Examples:
/path/to/this/repo/bin/control.sh My--Desk-lamp off
/path/to/this/repo/bin/control.sh my--desk-lamp disable
/path/to/this/repo/bin/control.sh "My  Desk Lamp" on

/path/to/this/repo/bin/control.sh hutch-lights   on
/path/to/this/repo/bin/control.sh "Hutch Lights" enable
/path/to/this/repo/bin/control.sh hutch-lights   off
```

## Advanced Usage

This section describes the `cli.py` command line interface and its various
options.

### Discovery

To discover devices in your network using `SSDP`, you can just run the
`scan` or `discover` command or one of its variants.

The discovery commands will store the discovered device information
in a local registry (`config/registry.json`).

```shell
/path/to/this/repo/cli.py -c scan  #  or -c discover

# These options will also work as a variation of the above command.
/path/to/this/repo/cli.py -s  #  or --scan or --discover
```

### List Devices

To list the devices, use the `list` command.

```shell
/path/to/this/repo/cli.py -c list
```

### Device Information

To get details about a device, use the `info` command along with a device
name.

```shell
/path/to/this/repo/cli.py -d 'my--desk-lamp' -c info
```

### Update Registry

To update the device registry, use the `update` command.

```shell
/path/to/this/repo/cli.py -c update
```

### Control a device

To control an individual device, specify the device name and a control
option (one of `on`, `off`, `enable`, `disable`).

```shell
/path/to/this/repo/cli.py -d My--Desk-lamp -c off
/path/to/this/repo/cli.py -d my--desk-lamp -c disable
/path/to/this/repo/cli.py -d "My  Desk Lamp" -c "on"

/path/to/this/repo/cli.py -d hutch-lights   -c on
/path/to/this/repo/cli.py -d "Hutch Lights" -c enable
/path/to/this/repo/cli.py -d hutch-lights   -c off
```
