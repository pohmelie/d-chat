from socket import *
from connection import Connection


class Bnet():
    PLATFORM_INTEL = 0x49583836
    PRODUCT_ID = b"PX2D"
    VERSION_BYTE = 0x0d
    PRODUCT_LANGUAGE = b"SUne"
    COUNTRY_ABREVIATION = b"RUS"
    COUNTRY = b"Russia"

    def __init__(self, host, port=6112, **kwargs):
        self.host = host
        self.port = port

        self.onlogin = kwargs.get("onlogin", None)  # onlogin -> result

    def login(self):
        self.con = Connection(self.onpacket)
        self.con.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.con.connect((self.host, self.port))

        self.push(b"\x01")  # some initialization

    def onpacket(self, data):
        pass
