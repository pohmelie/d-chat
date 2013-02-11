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

    kernel32 = ctypes.windll.kernel32

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
        local_ip=gethostbyname(gethostname()),
        time_zone=time.altzone // 60,
        locale_id=kernel32.GetUserDefaultLCID(),
        language_id=kernel32.GetUserDefaultLangID(),
        country_abreviation=b"RUS",
        country=b"Russia"
    )
    yoba = spacket.build(c)
    #print(rev(yoba))
    #print(spacket.parse(yoba))

    pack = rev("ff518b00aafcb600000d000177f1445a02000000000000001000000006000000e5d2d20000000000e665ded17d456b6816316fef65ff211697b11787100000000c0000003ada4a000000000072a8c0ac1d61d6b810f6faa5026f1453564a54c967616d652e6578652030322f30342f31332031323a34313a333420363535333600706f686d656c69653900")
    print(spacket.parse(pack))
    print(spacket.build(spacket.parse(pack)) == pack)
