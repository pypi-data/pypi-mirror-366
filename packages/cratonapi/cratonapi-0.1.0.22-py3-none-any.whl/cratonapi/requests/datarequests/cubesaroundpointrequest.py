import struct


def request(x: float, y: float, radius: float) -> bytes:
    signature = int.from_bytes(str.encode("WSPM"), "little")
    size = 28
    operation = 2
    request_id = 21
    uid = 0
    return struct.pack(
        "<IIHHIddf", signature, size, operation, request_id, uid, x, y, radius
    )
