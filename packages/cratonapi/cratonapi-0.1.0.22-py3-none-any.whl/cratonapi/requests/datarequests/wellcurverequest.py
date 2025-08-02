import struct


def request(well_id: int, curve_id: int) -> bytes:
    signature = int.from_bytes(str.encode("WSPM"), "little")
    size = 16
    operation = 2
    request_id = 29
    uid = 0
    return struct.pack(
        "<IIHHIII", signature, size, operation, request_id, uid, well_id, curve_id
    )
