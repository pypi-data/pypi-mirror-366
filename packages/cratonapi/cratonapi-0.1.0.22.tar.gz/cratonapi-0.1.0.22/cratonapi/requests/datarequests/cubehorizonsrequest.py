import struct


def request(cube_id: int) -> bytes:
    signature = int.from_bytes(str.encode("WSPM"), "little")
    size = 12
    operation = 2
    request_id = 18
    uid = 0
    return struct.pack("<IIHHII", signature, size, operation, request_id, uid, cube_id)
