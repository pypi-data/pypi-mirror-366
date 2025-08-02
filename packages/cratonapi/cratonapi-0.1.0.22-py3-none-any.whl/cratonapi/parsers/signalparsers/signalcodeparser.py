import struct

from cratonapi.parsers.signalparsers import \
    griddisplaypropertieschangesignalparser
from cratonapi.signals import *


def parse(message: bytes) -> AbstractSignal:
    if len(message) < 12:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, signal_id = struct.unpack("<IHH", message[4:12])
    if operation != 4:
        raise RuntimeError("Message is not a signal!")
    match signal_id:
        case SignalType.grid_list_changed:
            return GridListChangedSignal()
        case SignalType.grid_display_properties_changed:
            grid_id = griddisplaypropertieschangesignalparser.parse(message)
            return GridDisplayPropertiesChangedSignal(grid_id)
        case SignalType.well_list_changed:
            return WellListChangedSignal()
        case _:
            return AbstractSignal()
