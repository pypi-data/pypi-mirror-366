import struct


def request(
    cube_id: int,
    horizon_top_name: str,
    horizon_bot_name: str,
    top_off: float,
    bot_off: float,
    start_inline_idx: int,
    end_inline_idx: int,
    start_crossline_idx: int,
    end_crossline_idx: int,
) -> bytes:
    name_top_size = len(horizon_top_name)
    name_bot_size = len(horizon_bot_name)
    signature = int.from_bytes(str.encode("WSPM"), "little")
    size = 40 + name_top_size + name_bot_size
    operation = 2
    request_id = 19
    uid = 0
    message = bytearray()
    message.extend(
        struct.pack(
            "<IIHHIIH",
            signature,
            size,
            operation,
            request_id,
            uid,
            cube_id,
            name_top_size,
        )
    )
    if name_top_size > 0:
        top_byte_name = horizon_top_name.encode("cp1251")
        for i in range(name_top_size):
            message.extend(struct.pack("B", top_byte_name[i]))
    message.extend(struct.pack("H", name_bot_size))
    if name_bot_size > 0:
        bot_byte_name = horizon_bot_name.encode("cp1251")
        for i in range(name_bot_size):
            message.extend(struct.pack("B", bot_byte_name[i]))
    message.extend(
        struct.pack(
            "<ddHHHH",
            top_off,
            bot_off,
            start_inline_idx,
            end_inline_idx,
            start_crossline_idx,
            end_crossline_idx,
        )
    )
    return message
