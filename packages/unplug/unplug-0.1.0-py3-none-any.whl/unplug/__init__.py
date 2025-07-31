# SPDX-License-Identifier: GPL-3.0-or-later

from collections import defaultdict
from typing import Self
from dataclasses import dataclass
from pathlib import Path

import libevdev
import logging
import dataclasses
import itertools
import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_device_ids = itertools.count(1)
_sequence_ids = itertools.count(1)


@dataclass(frozen=True)
class EvdevUsage:
    type: int
    code: int

    @property
    def evbit(self) -> libevdev.EventCode:
        return libevdev.evbit(self.type, self.code)  # type: ignore


@dataclass(frozen=True)
class AbsInfo:
    minimum: int
    maximum: int
    fuzz: int
    flat: int
    resolution: int


@dataclass(frozen=True)
class InputEvent:
    usecs: int
    usage: EvdevUsage
    value: int

    @classmethod
    def from_quartuple(
        cls, sec: int, usec: int, type: int, code: int, value: int
    ) -> Self:
        return cls(
            usecs=sec * 1_000_000 + usec, usage=EvdevUsage(type, code), value=value
        )


@dataclass(eq=True)
class Device:
    name: str
    bustype: int
    vid: int
    pid: int
    evbits: list[EvdevUsage] = dataclasses.field(repr=False)
    absinfo: dict[EvdevUsage, AbsInfo] = dataclasses.field(repr=False)
    props: list[int] = dataclasses.field(repr=False)

    id: int = dataclasses.field(
        init=False, repr=False, compare=False, default_factory=lambda: next(_device_ids)
    )

    _uinput: libevdev.Device | None = dataclasses.field(
        init=False, repr=False, compare=False, default=None
    )

    def __hash__(self):
        return hash((self.name, self.bustype, self.vid, self.pid))

    @property
    def is_plugged(self) -> bool:
        return self._uinput is not None

    @property
    def devnode(self) -> str:
        return self._uinput.devnode

    def plug(self):
        if self._uinput is not None:
            return

        dev = libevdev.Device()
        dev.name = self.name
        dev.id = {
            "bustype": self.bustype,
            "vendor": self.vid,
            "product": self.pid,
        }
        for bit in self.evbits:
            if bit.type == libevdev.EV_ABS.value:
                absinfo = libevdev.InputAbsInfo(
                    minimum=self.absinfo[bit].minimum,
                    maximum=self.absinfo[bit].maximum,
                    fuzz=self.absinfo[bit].fuzz,
                    flat=self.absinfo[bit].flat,
                    resolution=self.absinfo[bit].resolution,
                )
            elif bit.type == libevdev.EV_REP.value:
                if bit.code == libevdev.EV_REP.REP_DELAY.value:
                    absinfo = 255
                elif bit.code == libevdev.EV_REP.REP_PERIOD.value:
                    absinfo = 33
            else:
                absinfo = None
            dev.enable(libevdev.evbit(bit.type, bit.code), absinfo)

        for prop in self.props:
            dev.enable(libevdev.propbit(prop))

        self._uinput = dev.create_uinput_device()
        logger.debug(f"Created uinput device: {self._uinput.devnode}")

    def unplug(self):
        if self._uinput:
            del self._uinput

    def send_events(self, events: list[InputEvent]):
        if self._uinput is None:
            logger.error("Device has not been created yet")
            return

        es = [
            libevdev.InputEvent(
                libevdev.evbit(e.usage.type, e.usage.code), value=e.value
            )
            for e in events
        ]
        self._uinput.send_events(es)


@dataclass
class EventSequence:
    name: str
    description: str | None
    device: Device
    events: list[InputEvent]

    id: int = dataclasses.field(
        init=False, repr=False, default_factory=lambda: next(_sequence_ids)
    )


@dataclass
class LibinputRecording:
    device: Device
    sequence: EventSequence

    @classmethod
    def from_dict(cls, data: dict, /, fallback_name: str) -> Self:
        if "libinput" not in data:
            raise ValueError("data is not a libinput recording")

        if data.get("ndevices", 0) != 1:
            raise ValueError("libinput recording must contain exactly one device")

        try:
            device = data["devices"][0]
            evdev = device["evdev"]
            name = evdev["name"]
            bustype, vid, pid, _ = evdev["id"]

            evbits = [EvdevUsage(t, c) for t, cs in evdev["codes"].items() for c in cs]
            absinfos = {
                EvdevUsage(0x3, code): AbsInfo(*absinfo)
                for code, absinfo in evdev.get("absinfo", {}).items()
            }

            sequence_name = data.get("unplug", {}).get("name", fallback_name)
            sequence_description = data.get("unplug", {}).get("description", None)
            events = []
            for e in device["events"] or []:
                for event in e["evdev"]:
                    events.append(InputEvent.from_quartuple(*event))

            if not events:
                sequence_name = "<empty>"

            # If the first event has a nonzero offset, adjust all
            # events down
            if events and (offset := events[0].usecs) >= 0:
                events = [
                    InputEvent(usecs=e.usecs - offset, usage=e.usage, value=e.value)
                    for e in events
                ]

            device = Device(
                name=name,
                bustype=bustype,
                vid=vid,
                pid=pid,
                evbits=evbits,
                absinfo=absinfos,
                props=evdev["properties"],
            )
            sequence = EventSequence(
                name=sequence_name,
                description=sequence_description,
                events=events,
                device=device,
            )

            return cls(device=device, sequence=sequence)
        except KeyError as e:
            raise ValueError(f"Missing key in data: {e}")


@dataclass
class Unplug:
    device_sequences: dict[Device, list[EventSequence]]
    sequences: dict[int, EventSequence]
    devices: dict[int, Device]

    @classmethod
    def load_from_directory(cls, directory: Path = Path(".")) -> Self:
        """Load an instance from the given directory"""
        device_sequences = defaultdict(list)
        sequences = {}
        devices = {}
        for device_file in directory.glob("*.yml"):
            if device_file.is_dir() or device_file.name.startswith("."):
                continue

            data = yaml.safe_load(device_file.read_text(encoding="utf-8"))
            try:
                recording = LibinputRecording.from_dict(
                    data, fallback_name=device_file.name
                )
            except ValueError as e:
                logger.error(f"Error parsing file {device_file.name}: {e}")
                continue

            device = devices.setdefault(recording.device, recording.device)

            sequence = recording.sequence
            sequence.device = device
            sequences[sequence.id] = sequence

            device_sequences[device].append(recording.sequence)

        return cls(
            devices={d.id: d for d in devices},
            device_sequences=device_sequences,
            sequences=sequences,
        )
