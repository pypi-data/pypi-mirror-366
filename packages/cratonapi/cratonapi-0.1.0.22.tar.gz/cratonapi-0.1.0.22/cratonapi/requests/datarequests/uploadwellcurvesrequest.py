import struct

from cratonapi.datacontainers import WellCurve


def request(well_curve: WellCurve, well_id: int) -> bytes:
    signature = int.from_bytes(str.encode("WSPM"), "little")
    start_byte = 18
    byte = 8
    name_size = len(well_curve.curve_name)
    number_of_counts = well_curve.point_values.shape[0]
    size = start_byte + name_size + byte * number_of_counts * 2
    operation = 5
    request_id = 2
    message = bytearray()
    message.extend(
        struct.pack(
            "<IIHHIIH",
            signature,
            size,
            operation,
            request_id,
            well_id,
            well_curve.curve_type,
            name_size,
        )
    )
    message.extend(well_curve.curve_name.encode("cp1251"))
    message.extend(struct.pack("<I", number_of_counts))
    for i in range(number_of_counts):
        message.extend(
            struct.pack("<dd", well_curve.point_values[i], well_curve.point_depths[i])
        )
    return message
