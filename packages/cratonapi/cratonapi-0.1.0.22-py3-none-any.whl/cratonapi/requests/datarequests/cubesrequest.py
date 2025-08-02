import struct


def request() -> bytes:
    signature = int.from_bytes(str.encode("WSPM"), "little")
    size = 8
    operation = 2
    request_id = 17
    uid = 0
    return struct.pack("<IIHHI", signature, size, operation, request_id, uid)
