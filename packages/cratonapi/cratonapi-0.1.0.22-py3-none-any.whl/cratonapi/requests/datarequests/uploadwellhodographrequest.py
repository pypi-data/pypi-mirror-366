import struct

from cratonapi.datacontainers import WellHodograph


def request(well_id: int, hodograph: WellHodograph) -> bytes:
    signature = int.from_bytes(str.encode("WSPM"), "little")
    start_byte = 12
    byte = 8
    number_of_points = hodograph.point_times.shape[0]
    size = start_byte + 2 * byte * number_of_points
    operation = 5
    request_id = 6
    message = bytearray()
    message.extend(
        struct.pack(
            "<IIHHII", signature, size, operation, request_id, well_id, number_of_points
        )
    )
    for i in range(number_of_points):
        message.extend(
            struct.pack("<dd", hodograph.point_depths[i], hodograph.point_times[i])
        )
    return message
