from construct import *
from construct.adapters import *
from construct.macros import *
from construct.protocols.layer3.ipv4 import IpAddress


rpacket = Struct(
    "rpackets",
    Const(ULInt8(None), 0xff),
    Enum(
        ULInt8("packet_id"),
        SID_PING=0x25,
        SID_AUTH_INFO=0x50,
        SID_AUTH_CHECK=0x51,
        SID_LOGONRESPONSE2=0x3a,
        SID_ENTERCHAT=0x0a,
        SID_GETCHANNELLIST=0x0b,
        SID_CHATEVENT=0x0f,
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
                ),
                "SID_AUTH_CHECK": Struct(
                    None,
                    ULInt32("result"),
                    CString("info"),
                ),
                "SID_LOGONRESPONSE2": Struct(
                    None,
                    ULInt32("result"),
                    Optional(CString("info")),
                ),
                "SID_ENTERCHAT": Struct(
                    None,
                    CString("unique_name"),
                    CString("statstring"),
                    CString("account_name"),
                ),
                "SID_GETCHANNELLIST": Struct(
                    None,
                    OptionalGreedyRange(CString("channels")),
                ),
                "SID_CHATEVENT": Struct(
                    None,
                    Enum(
                        ULInt32("event_id"),
                        ID_USER=0x01,
                        ID_JOIN=0x02,
                        ID_LEAVE=0x03,
                        ID_WHISPER=0x04,
                        ID_TALK=0x05,
                        ID_BROADCAST=0x06,
                        ID_CHANNEL=0x07,
                        ID_USERFLAGS=0x09,
                        ID_WHISPERSENT=0x0a,
                        ID_CHANNELFULL=0x0d,
                        ID_CHANNELDOESNOTEXIST=0x0e,
                        ID_CHANNELRESTRICTED=0x0f,
                        ID_INFO=0x12,
                        ID_ERROR=0x13,
                        ID_EMOTE=0x17,
                        ID_SYSTEMBLUE=0x18,
                        ID_SYSTEMRED=0x19,
                    ),
                    ULInt32("user_flags"),
                    ULInt32("ping"),
                    IpAddress("ip_address"),
                    ULInt32("account_number"),
                    ULInt32("registration_authority"),
                    CString("username"),
                    CString("text"),
                ),
            }
        )
    )
)

rpackets = Struct(
    None,
    OptionalGreedyRange(rpacket),
    ExprAdapter(
        OptionalGreedyRange(Byte("tail")),
        encoder=lambda obj, ctx: list(obj),
        decoder=lambda obj, ctx: bytes(obj)
    )
)


if __name__ == "__main__":
    from recipe import *
    import time
    import ctypes
    from socket import *

    kernel32 = ctypes.windll.kernel32

    pack = rev("ff5067000000000023a059463e250000809a5600705fc7017665722d495838362d332e6d707100413d38303339333537353520423d3334303731393939353420433d33343835323638343437203420413d415e5320423d422b4320433d435e4120413d412d4200")
    #print(rpackets.parse(pack))
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
    #print(rpacket.parse(pack))
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

    pack = rev("ff0f300007000000010000001506000000000000baadf00d0df0adba706f686d656c69653900446961626c6f20494900")
    #print(rpacket.parse(pack))

    pack = rev("ff0f2b0001000000000000001506000000000000baadf00d0df0adba706f686d656c696539005058324400ff0f5d000100000000000000e100000000000000baadf00d0df0adba6b362d3100505832445275626174746c652e6e65742c50777777507777772c8b80390201010135ff510202ff024d46464646ffffff4646ff55e09e808001ffff00ff0f640001000000000000007300000000000000baadf00d0df0adba726d643936363600505832445275626174746c652e6e65742c586c6f705973686543486b612c8b8039020101010fff520202ff024d46464646ffffff4646ff5ae09e808001ffff00ff0f680001000000000000001600000000000000baadf00d0df0adba68657865646573696d616c00505832445275626174746c652e6e65742c54656c6f6872616e6974656c2c8b803d0202030114ff5d0303ff04e2ffffffffffffffffffff58e09a808001ffff00ff0f640001000000000000009100000000000000baadf00d0df0adba7a625f72756e657300505832445275626174746c652e6e65742c7a625f546f7052756e65732c8b80ffffffffffffffffffffff04ffffffffffffffffffffff01e080808001ffff00ff0f610001000000000000000300000000000000baadf00d0df0adba6c65646f76696b3200505832445275626174746c652e6e65742c6c65642d67656d732c8b80ffffffffff11ff4fffffff04ffffffffffffffffffffff01e080808001ffff00ff0f650001000000000000001500000000000000baadf00d0df0adba5a5f525f445f4e00505832445275626174746c652e6e65742c546865426573744f66576172732c8b8039020203010fff5c0303ff044dffffffffffffffffffff5fe09e808001ffff00ff0f600001000000000000005c01000000000000baadf00d0df0adba6170616e63757800505832445275626174746c652e6e65742c6e637578626c697a2c8b803e0202030105ff510303ff0251ffffffffa5ffffffffff60e09e808001ffff00ff0f630001000000000000008800000000000000baadf00d0df0adba686f726f73686f6b00505832445275626174746c652e6e65742c4a756e696f72727272722c8b803d0203030304ff520303ff05e10101010143ff010101ff2ce086808001ffff00ff0f650001000000000000001e00000000000000baadf00d0df0adba756e657863656c6c656400505832445275626174746c652e6e65742c756e657863656c6c65642c8b80ffffffffffffffffffffff06ffffffffffffffffffffff01e080808001ffff00ff0f670001000000000000000d00000000000000baadf00d0df0adba5b33357275735d00505832445275626174746c652e6e65742c4f74736f735f506574726f766963682c8b803d0101010104ff5d0202ff04e2ffffffffffffffffffff5be09e808001ffff00ff0f650001000000000000008300000000000000baadf00d0df0adba63686f636f6c6174657300505832445275626174746c652e6e65742c43686f636f6c617465732c8b80ff01010101ff2fff0202ff02ffffffffffffffffffffff54e09a808001ffff00ff0f610001000000000000004100000000000000baadf00d0df0adba657468696f70696100505832445275626174746c652e6e65742c457468696f7069612c8b80ff010202011cff510202ff01ffffffffffffffffffffff61e09e808001ffff00ff0f660001000000000000000500000000000000baadf00d0df0adba76656e6963655f717565656e00505832445275626174746c652e6e65742c446565705f4b69636b2c8b80ffffffffffffffffffffff04ffffffffffffffffffffff58e09e808001ffff00ff0f5f000100000000000000a100000000000000baadf0")
    print(rpackets.parse(pack))
