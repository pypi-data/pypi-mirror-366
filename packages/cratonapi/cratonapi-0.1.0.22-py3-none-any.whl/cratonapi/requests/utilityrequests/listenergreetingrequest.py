import struct


def request(signals_to_listen: tuple) -> bytes:
    signature = int.from_bytes(str.encode("WSPM"), "little")
    operation = 1
    app_id = 0
    size = 5 + 2 * len(signals_to_listen)
    return struct.pack(
        f"<IIHBH{len(signals_to_listen)}H",
        signature,
        size,
        operation,
        app_id,
        len(signals_to_listen),
        *signals_to_listen,
    )
