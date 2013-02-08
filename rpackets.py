from construct import *
from construct.adapters import *
from construct.macros import *


rpacket = Struct(
    None,
    Const(ULInt8(None), 0xff),
    Enum(
        ULInt8("packet_id"),
        SID_PING=0x25,
        SID_AUTH_INFO=0x50,
    ),
    ULInt16("length"),
    Embed(
        Switch(
            None,
            lambda ctx: ctx.packet_id,
            {
                "SID_PING": Struct(
                    None,
                    ULInt32("value"),
                ),
                "SID_AUTH_INFO": Struct(
                    None,
                    ULInt32("logon_type"),
                    ULInt32("server_token"),
                    ULInt32("udp_value"),
                    Bytes("file_time", 8),
                    CString("file_name"),
                    CString("seed_values")
                )
            }
        )
    )
)

rpackets = OptionalGreedyRange(rpacket)  # server -> client (multiply packets)


if __name__ == "__main__":
    from recipe import *
    import time
    import ctypes
    from socket import *

    kernel32 = ctypes.windll.kernel32

    pack = rev("ff 25 08 00 e6 68 b6 25")
    print(rpackets.parse(pack))
    print(rpackets.build(rpackets.parse(pack)) == pack)

    pack = rev("ff506700000000006d2cec26330e0000809a5600705fc7017665722d495838362d332e6d707100413d38303339333537353520423d3334303731393939353420433d33343835323638343437203420413d415e5320423d422b4320433d435e4120413d412d4200")
    print(rpackets.parse(pack))
    print(rpackets.build(rpackets.parse(pack)) == pack)
