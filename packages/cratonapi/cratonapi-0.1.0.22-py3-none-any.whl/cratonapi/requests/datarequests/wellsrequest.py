import struct


def request(count: int, *wells_ids: int) -> bytes:
    signature = int.from_bytes(str.encode("WSPM"), "little")
    size = 10 + count * 4
    operation = 2
    request_id = 2
    uid = 0
    if count == 0:
        return struct.pack(
            "<IIHHIH", signature, size, operation, request_id, uid, count
        )
    elif count == 1:
        return struct.pack(
            "<IIHHIHI", signature, size, operation, request_id, uid, count, wells_ids[0]
        )
    else:
        return struct.pack(
            f"<IIHHIH{count}I",
            signature,
            size,
            operation,
            request_id,
            uid,
            count,
            *wells_ids,
        )
