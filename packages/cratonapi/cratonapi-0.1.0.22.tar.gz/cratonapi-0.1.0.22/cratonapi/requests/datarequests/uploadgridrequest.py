import struct

from cratonapi.datacontainers import Grid


def request(name: str, grid: Grid) -> bytes:
    signature = int.from_bytes(str.encode("WSPM"), "little")
    start_byte = 66
    byte = 8
    name_size = len(name)
    size = start_byte + name_size + byte * grid.n_x * grid.n_y
    operation = 5
    request_id = 1
    message = bytearray()
    message.extend(
        struct.pack("<IIHHH", signature, size, operation, request_id, name_size)
    )
    message.extend(name.encode("cp1251"))
    message.extend(
        struct.pack(
            "<HHddddddd",
            grid.n_x,
            grid.n_y,
            grid.x_min,
            grid.x_max,
            grid.y_min,
            grid.y_max,
            grid.z_min,
            grid.z_max,
            grid.blank_code,
        )
    )
    for value in grid.data:
        message.extend(struct.pack("d", value))
    return message
