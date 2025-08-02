import struct


def request(app_id: int = 1) -> bytes:
    signature = int.from_bytes(str.encode("WSPM"), "little")
    operation = 1
    size = 3
    return struct.pack("<IIHB", signature, size, operation, app_id)
