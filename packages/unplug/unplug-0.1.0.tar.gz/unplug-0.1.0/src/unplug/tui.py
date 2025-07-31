# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from rich.text import Text
from textual import on
from textual.binding import Binding
from textual.app import App, ComposeResult
from textual.containers import (
    Horizontal,
    Vertical,
)
from textual.events import Mount
from textual.widgets import (
    Header,
    Footer,
    DataTable,
    Markdown,
    SelectionList,
    RichLog,
)
from textual.widgets.selection_list import Selection

import asyncio
import libevdev
import logging
import time

from . import Unplug, Device, EventSequence

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LogPanel(RichLog):
    """A panel that shows log messages."""

    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
    ]

    def on_mount(self) -> None:
        """Configure the log panel when mounted."""

        self.border_title = "Log"

        # Remove all existing handlers to prevent stdout/stderr output
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[
            :
        ]:  # slice copy to avoid modification during iteration
            root_logger.removeHandler(handler)

        # Create a handler that writes to this widget
        class TextualHandler(logging.Handler):
            def __init__(self, log_panel: "LogPanel"):
                super().__init__()
                self.log_panel = log_panel

            def emit(self, record: logging.LogRecord):
                try:
                    msg = self.format(record)
                    self.log_panel.write(msg)
                except Exception:
                    self.handleError(record)

        # Add our custom handler to the logger
        handler = TextualHandler(self)
        handler.setFormatter(
            logging.Formatter("%(relativeCreated)5d %(levelname).8s|%(message)s")
        )
        logger.addHandler(handler)


class DeviceList(SelectionList):
    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
    ]

    def __init__(self, unplug: Unplug):
        devices = list(
            Selection(d.name, idx, False, id=str(d.id))
            for idx, d in enumerate(unplug.devices.values())
        )
        super().__init__(*devices)
        self.border_title = "Devices"


class DeviceDetails(DataTable):
    def __init__(self, unplug: Unplug):
        super().__init__()
        self.unplug = unplug
        self.can_focus = False
        self.border_title = "Device Details"
        self.show_header = False

    def on_mount(self) -> None:
        self.add_columns("Details", "Value")

    def update_details(self, device: Device):
        bustypes = {
            0x01: "PCI",
            0x02: "ISAPNP",
            0x03: "USB",
            0x04: "HIL",
            0x05: "BLUETOOTH",
            0x06: "VIRTUAL",
            0x10: "ISA",
            0x11: "I8042",
            0x12: "XTKBD",
            0x13: "RS232",
            0x14: "GAMEPORT",
            0x15: "PARPORT",
            0x16: "AMIGA",
            0x17: "ADB",
            0x18: "I2C",
            0x19: "HOST",
            0x1A: "GSC",
            0x1B: "ATARI",
            0x1C: "SPI",
            0x1D: "RMI",
            0x1E: "CEC",
            0x1F: "INTEL_ISHTP",
            0x20: "AMD_SFH",
        }

        self.clear()
        self.add_row("Bus", bustypes.get(device.bustype, "???"))
        self.add_row("ID", f"{device.vid:04x}:{device.pid:04x}")
        if device.is_plugged:
            self.add_row("Node", device.devnode)


class EventList(DataTable):
    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
    ]

    def __init__(self, unplug: Unplug):
        super().__init__()
        self.unplug = unplug
        self.cursor_type = "row"
        self.border_title = "Sequences"

    def on_mount(self) -> None:
        self.add_columns("Sequences")
        self.show_header = False

    def update_list(self, device: Device):
        self.clear()

        for sequence in self.unplug.device_sequences[device]:
            self.add_row(sequence.name, key=str(sequence.id))


class EventSequenceDetails(Markdown):
    def __init__(self, unplug: Unplug):
        super().__init__("No sequence selected.")
        self.unplug = unplug
        self.can_focus = False
        self.border_title = "Sequence Details"

    def update_details(self, sequence: EventSequence):
        self.update(sequence.description or "No description available.")


class EventSequenceEvents(DataTable):
    def __init__(self, unplug: Unplug):
        super().__init__()
        self.unplug = unplug
        self.can_focus = False
        self.cursor_type = "row"
        self.border_title = "Events"

    def on_mount(self) -> None:
        self.add_column("Timestamp")
        self.add_column("Delta time (ms)")
        self.add_column("Type")
        self.add_column("Code")
        self.add_column("Value")

    def update_events(self, sequence: EventSequence):
        self.clear()
        last_time = 0
        for event in sequence.events:
            evbit = (
                event.usage.evbit
            )  # libevdev.evbit(event.usage.type, event.usage.code)
            assert evbit is not None

            sec = event.usecs // 1_000_000
            usec = event.usecs % 1_000_000
            delta = (event.usecs - last_time) // 1_000
            if evbit.type == libevdev.EV_SYN:
                last_time = event.usecs
            self.add_row(
                f"{sec:3d}.{usec:06d}",
                Text(
                    f"{delta:+3d}ms" if evbit.type == libevdev.EV_SYN else "",
                    justify="right",
                ),
                evbit.type.name,
                evbit.name,
                Text(f"{event.value}", justify="right"),
            )


class UnplugApp(App):
    CSS = """

    LogPanel {
        height: 15;
        dock: bottom;
        border: solid $primary;
    }

    EventList {
        height: 100%;
        border: solid $primary;
        padding-top: 1;
    }

    DeviceList {
        height: 100%;
        border: solid $primary;
        padding: 1;
    }

    DeviceDetails {
        height: 12;
        dock: bottom;
        border: solid $primary;
        padding-top: 1;
    }

    EventSequenceDetails {
        height: 12;
        dock: bottom;
        border: solid $primary;
        padding: 1;
    }

    EventSequenceEvents {
        width: 100%;
        text-align: right;
        border: solid $primary;
        padding: 1;
    }

    Widget :focus {
        border: solid $accent;
    }

    #first_vertical {
        width: 36
    }

    #second_vertical {
        width: 40
    }

    #main-content {
        width: 100%;
        layout: horizontal;
        border: solid $primary;
    }
    """

    BINDINGS = [Binding("ctrl+q", "quit", "Quit", show=True, priority=True)]

    def __init__(self, unplug: Unplug):
        super().__init__()
        self.title = "unplug"
        self.unplug = unplug

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Horizontal(id="main-content"):
                with Vertical(id="first_vertical"):
                    yield DeviceList(self.unplug)
                    yield DeviceDetails(self.unplug)
                with Vertical(id="second_vertical"):
                    yield EventList(self.unplug)
                    yield EventSequenceDetails(self.unplug)
                with Vertical(id="third_vertical"):
                    yield EventSequenceEvents(self.unplug)
            yield LogPanel()
        yield Footer()

    @on(SelectionList.SelectionToggled)
    def create_uinput_device(self, event) -> None:
        slist = event.selection_list
        selections = [
            slist.get_option_at_index(idx) for idx in event.selection_list.selected
        ]

        selected_device_ids = [int(s.id) for s in selections]
        for device in [d for d in self.unplug.devices.values() if d.is_plugged]:
            if device.id not in selected_device_ids:
                logger.debug(f"Unplugging {device.name}")
                device.unplug()

        for deviceid in selected_device_ids:
            device = self.unplug.devices[int(deviceid)]
            if not device.is_plugged:
                logger.debug(f"Plugging {device.name}")
                device.plug()

    @on(Mount)
    @on(SelectionList.SelectionHighlighted)
    def update_device_details(self, _) -> None:
        highlighted = self.query_one(SelectionList).highlighted
        if highlighted is None:
            return

        selection = self.query_one(SelectionList).get_option_at_index(highlighted)
        assert selection.id is not None
        device = self.unplug.devices[int(selection.id)]
        self.query_one(DeviceDetails).update_details(device)
        self.query_one(EventList).update_list(device)

    @on(EventList.RowHighlighted)
    def update_event_sequence(self, event) -> None:
        # Key is the sequence ID
        key = event.row_key.value if event.row_key else None
        if key is None:
            return

        if (s := self.unplug.sequences.get(int(key), None)) is not None:
            self.query_one(EventSequenceEvents).update_events(s)
            self.query_one(EventSequenceDetails).update_details(s)

    @on(EventList.RowSelected)
    async def replay_sequence(self, event) -> None:
        # Key is the sequence ID
        key = event.row_key.value if event.row_key else None
        if key is None:
            return

        if (s := self.unplug.sequences.get(int(key), None)) is None:
            return

        device = self.unplug.devices[s.device.id]
        if not device.is_plugged:
            return

        logger.debug("Replaying sequence")
        now = time.time() * 1_000_000  # µs
        initial_time = now

        details_data_table = self.query_one(EventSequenceEvents)

        for idx, event in enumerate(s.events):
            now = time.time() * 1_000_000  # µs
            target_time = initial_time + event.usecs
            delay = target_time - now
            if delay > 10_000:
                if delay > 1_000_000:
                    logger.debug(f"delaying by {delay / 1_000_000:.3f}s")
                await asyncio.sleep((delay - 1_000) / 1_000_000)
                now = time.time() * 1_000_000  # µs

            device.send_events([event])
            if event.usage.evbit.type == libevdev.EV_SYN:
                details_data_table.move_cursor(row=idx)

        details_data_table.move_cursor(row=0)


def main():
    try:
        with open("/dev/uinput", "wb"):
            pass
    except PermissionError:
        logger.error("Cannot write to /dev/uinput, exiting")
        return

    recordings_dir = Path("recordings")
    if not recordings_dir.exists():
        recordings_dir = Path(".")

    unplug = Unplug.load_from_directory(recordings_dir)
    if not unplug.devices:
        logger.error("No devices found in this directory.")
        return
    app = UnplugApp(unplug)
    app.run()


if __name__ == "__main__":
    main()
