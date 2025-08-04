# unplug

`unplug` is a Python TUI that allows creating and replaying uinput devices from
libinput recordings.

`unplug` requires write access to `/dev/uinput`, so it needs to be run as root or
with the appropriate permissions set on the `/dev/uinput` node.


## Installation

```bash
$ pip install unplug
# allow access to uinput for the time being (or run as root)
$ sudo chmod o+rw /dev/uinput
$ unplug
```

This will search for any `.yml` file in the current directory and if
it looks like a valid `libinput record` file, it will load it into
the available list of devices.

Where the device name/vid/pid is the same, multiple recordings are collated
into the same device within unplug, so the

See the
[libinput documentation](https://wayland.freedesktop.org/libinput/doc/latest/tools.html#libinput-record-and-libinput-replay)
for details on `libinput record`.

## Running from git

```bash
$ git clone https://gitlab.freedesktop.org/whot/unplug.git
$ cd unplug
$ uv run unplug
```

## Updating recordings

To create recordings, you can use the `libinput record` command:

```bash
$ sudo libinput record --output recording.yml
# select device, record a few events, ctrl+c
```

Adding the (optional) `unplug.name` and `unplug.description` keys to the
recording file will allow you to name the recording in the unplug TUI:

```yaml
# libinput record
version: 1
ndevices: 1
libinput:
  version: "1.28.903"
  git: "unknown"
# Add the unplug.name key as description of this recording
unplug:
  name: "Key A press/release"
  description: any short markdown
````
