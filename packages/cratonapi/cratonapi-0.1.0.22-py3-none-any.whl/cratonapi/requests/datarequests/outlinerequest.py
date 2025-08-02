import struct


def request(outline_id: int) -> bytes:
    signature = int.from_bytes(str.encode("WSPM"), "little")
    size = 12
    operation = 2
    request_id = 31
    uid = 0
    return struct.pack(
        "<IIHHII", signature, size, operation, request_id, uid, outline_id
    )
