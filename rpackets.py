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

    pack = rev("ff5067000000000023a059463e250000809a5600705fc7017665722d495838362d332e6d707100413d38303339333537353520423d3334303731393939353420433d33343835323638343437203420413d415e5320423d422b4320433d435e4120413d412d4200")
    print(rpackets.parse(pack))
    '''
Container:
    length = 103
    packet_id = 'SID_AUTH_INFO'
    seed_values = b'A=803935755 B=3407199954 C=3485268447 4 A=A^S B=B+C C=C^A A=A-B'
    udp_value = 9534
    file_time = b'\x80\x9aV\x00p_\xc7\x01'
    file_name = b'ver-IX86-3.mpq'
    logon_type = 0
    server_token = 1180278819
    '''

# STEALTH

    pack = rev("ff50670000000000b7e1f97f6e210000809a5600705fc7017665722d495838362d332e6d707100413d38303339333537353520423d3334303731393939353420433d33343835323638343437203420413d415e5320423d422b4320433d435e4120413d412d4200")
    print(rpacket.parse(pack))
    '''
Container:
    logon_type = 0
    server_token = 2147082679
    udp_value = 8558
    packet_id = 'SID_AUTH_INFO'
    seed_values = b'A=803935755 B=3407199954 C=3485268447 4 A=A^S B=B+C C=C^A A=A-B'
    length = 103
    file_name = b'ver-IX86-3.mpq'
    file_time = b'\x80\x9aV\x00p_\xc7\x01'
    '''
