from construct import *
from construct.adapters import *
from construct.macros import *
from construct.protocols.layer3.ipv4 import IpAddress


class PacketLengthAdapter(Adapter):
    def _encode(self, obj, context):
        obj.length = 0
        obj.length = len(_spacket.build(obj))
        return obj

    def _decode(self, obj, context):
        return obj

_spacket = Struct(
    None,
    Const(ULInt8(None), 0xff),
    Enum(
        ULInt8("packet_id"),
        SID_AUTH_INFO=0x50,
        SID_PING=0x25,
        SID_AUTH_CHECK=0x51,
        SID_LOGONRESPONSE2=0x3a,
        SID_ENTERCHAT=0x0a,
        SID_GETCHANNELLIST=0x0b,
        SID_JOINCHANNEL=0x0c,
    ),
    ULInt16("length"),
    Embed(
        Switch(
            None,
            lambda ctx: ctx.packet_id,
            {
                "SID_AUTH_INFO": Struct(
                    None,
                    ULInt32("protocol_id"),
                    Bytes("platform_id", 4),
                    Bytes("product_id", 4),
                    ULInt32("version_byte"),
                    Bytes("product_language", 4),
                    IpAddress("local_ip"),
                    SLInt32("time_zone"),
                    ULInt32("locale_id"),
                    ULInt32("language_id"),
                    CString("country_abreviation"),
                    CString("country")
                ),
                "SID_PING": Struct(
                    None,
                    ULInt32("value"),
                ),
                "SID_AUTH_CHECK": Struct(
                    None,
                    ULInt32("client_token"),
                    ULInt32("exe_version"),
                    ULInt32("exe_hash"),
                    ULInt32("number_of_cd_keys"),
                    ULInt32("spawn_cd_key"),
                    Array(
                        lambda ctx: ctx["number_of_cd_keys"],
                        Struct(
                            "cd_keys",
                            ULInt32("key_length"),
                            ULInt32("cd_key_product"),
                            ULInt32("cd_key_public"),
                            Const(ULInt32(None), 0),
                            Bytes("hash", 5 * 4),
                        )
                    ),
                    CString("exe_info"),
                    CString("cd_key_owner")
                ),
                "SID_LOGONRESPONSE2": Struct(
                    None,
                    ULInt32("client_token"),
                    ULInt32("server_token"),
                    Bytes("hash", 5 * 4),
                    CString("username"),
                ),
                "SID_ENTERCHAT": Struct(
                    None,
                    CString("username"),
                    CString("statstring"),
                ),
                "SID_GETCHANNELLIST": Struct(
                    None,
                    Bytes("product_id", 4),
                ),
                "SID_JOINCHANNEL": Struct(
                    None,
                    ULInt32("unknown"),
                    CString("channel_name"),
                ),
            }
        )
    )
)

spacket = PacketLengthAdapter(_spacket)  # client -> server

if __name__ == "__main__":
    from recipe import *
    import time
    import ctypes
    from socket import *

    '''kernel32 = ctypes.windll.kernel32

    PLATFORM_INTEL = b"68XI"
    PRODUCT_ID = b"PX2D"
    VERSION_BYTE = 0x0d
    PRODUCT_LANGUAGE = b"SUne"

    c = Container(
        packet_id="SID_AUTH_INFO",
        protocol_id=0,
        platform_id=PLATFORM_INTEL,
        product_id=PRODUCT_ID,
        version_byte=VERSION_BYTE,
        product_language=PRODUCT_LANGUAGE,
        local_ip="192.168.0.100",
        time_zone=time.altzone // 60,
        locale_id=kernel32.GetUserDefaultLCID(),
        language_id=kernel32.GetUserDefaultLangID(),
        country_abreviation=b"RUS",
        country=b"Russia"
    )
    yoba = spacket.build(c)'''
    #print(rev(yoba))
    #print(spacket.parse(yoba))

    pack = rev("ff5033000000000036385849505832440d00000053556e650a00000a88ffffff19040000190400005255530052757373696100")
    print(spacket.parse(pack))
    '''
Container:
    country = b'Russia'
    product_id = b'PX2D'
    protocol_id = 0
    packet_id = 'SID_AUTH_INFO'
    platform_id = b'68XI'
    length = 51
    local_ip = '10.0.0.10'
    locale_id = 1049
    time_zone = -120
    version_byte = 13
    product_language = b'SUne'
    language_id = 1049
    country_abreviation = b'RUS'
    '''

    pack = rev("ff51860096a4d451000d000177f1445a02000000000000001000000006000000012ba40000000000d46848d2ba32773fbc78e3f8a53122b8ba19e12d100000000c0000002776620000000000c33d2b8f814ecb9bd93f843d52368aff5658d79447616d652e6578652031302f31382f31312032303a34383a313420363535333600796f626100")
    print(spacket.parse(pack))
    '''
Container:
    client_token = 1372890262
    number_of_cd_keys = 2
    cd_key_owner = b'yoba'
    exe_info = b'Game.exe 10/18/11 20:48:14 65536'
    cd_keys = [
        Container:
            cd_key_public = 10758913
            cd_key_product = 6
            key_length = 16
            hash = b'\xd4hH\xd2\xba2w?\xbcx\xe3\xf8\xa51"\xb8\xba\x19\xe1-'
        Container:
            cd_key_public = 6452775
            cd_key_product = 12
            key_length = 16
            hash = b'\xc3=+\x8f\x81N\xcb\x9b\xd9?\x84=R6\x8a\xffVX\xd7\x94'
    ]
    packet_id = 'SID_AUTH_CHECK'
    spawn_cd_key = 0
    exe_version = 16780544
    exe_hash = 1514467703
    length = 134
    '''


# STEALTH

    pack = rev("ff518b00ea7ebd6c000d000177f1445a02000000000000001000000007000000cd04ee000000000075d7b58af821e0360373c6521f6542efc59a12ab100000000c000000ab42d70000000000b8f8b9658b6e6c521f22ffc9745b7a21d845aa3867616d652e6578652030322f30342f31332032313a30303a303020363535333600706f686d656c69653900")
    print(spacket.parse(pack))
    '''
Container:
    client_token = 1824358122
    length = 139
    number_of_cd_keys = 2
    exe_info = b'game.exe 02/04/13 21:00:00 65536'
    cd_key_owner = b'pohmelie9'
    exe_version = 16780544
    packet_id = 'SID_AUTH_CHECK'
    spawn_cd_key = 0
    exe_hash = 1514467703
    cd_keys = [
        Container:
            hash = b'u\xd7\xb5\x8a\xf8!\xe06\x03s\xc6R\x1feB\xef\xc5\x9a\x12\xab'
            key_length = 16
            cd_key_public = 15598797
            cd_key_product = 7
        Container:
            hash = b'\xb8\xf8\xb9e\x8bnlR\x1f"\xff\xc9t[z!\xd8E\xaa8'
            key_length = 16
            cd_key_public = 14107307
            cd_key_product = 12
    ]
    '''
