import struct


def parse(message: bytes) -> int:
    if len(message) != 16:
        raise RuntimeError("Incomplete message!")
    grid_id = struct.unpack("<I", message[12:16])[0]
    return grid_id
