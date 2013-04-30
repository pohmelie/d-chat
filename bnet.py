import time
import logging

from construct import Container
from random import randint
from socket import socket

from spackets import spacket
from rpackets import rpackets
from bnutil import check_revision, hash_d2key, sub_double_hash, bsha1


class Bnet():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def login_error(self, packet_id, retcode):
        pass

    def chat_event(self, packet):
        pass

    def login(self, username, password):
        self.username = bytes(username, "ascii")
        self.hashpass = bsha1(bytes(password, "ascii"))

        self.head = b""

        self.sock = socket()
        try:
            self.sock.connect((self.host, self.port))
        except:
            self.login_error("Connecting to server")
            return

        self.sock.sendall(b"\x01")
        self.sock.sendall(
            spacket.build(
                Container(
                    packet_id="SID_AUTH_INFO",
                    protocol_id=0,
                    platform_id=b'68XI',
                    product_id=b'PX2D',
                    version_byte=13,
                    product_language=b'SUne',
                    local_ip="192.168.0.100",
                    time_zone=time.altzone // 60,
                    locale_id=1049,
                    language_id=1049,
                    country_abreviation=b'RUS',
                    country=b'Russia',
                )
            )
        )

    def on_packet(self):
        unparsed = rpackets.parse(self.head + self.sock.recv(2 ** 16))
        self.head = unparsed.tail

        if len(unparsed.rpackets) == 0:
            logging.info("[bnet.py] Nothing to proceed, but data there")

        for pack in unparsed.rpackets:

            if pack.packet_id == "SID_PING":
                self.sock.sendall(spacket.build(pack))

            elif pack.packet_id == "SID_AUTH_INFO":
                self.client_token = randint(10 * 60 * 1000, 2 ** 32 - 1)
                self.server_token = pack.server_token

                clpub, clhash = hash_d2key(b"DPTGEGHRPH4EB7EV", self.client_token, self.server_token)
                lodpub, lodhash = hash_d2key(b"KFE6H7RPTRTHDEJE", self.client_token, self.server_token)

                self.sock.sendall(
                    spacket.build(
                        Container(
                            packet_id="SID_AUTH_CHECK",
                            client_token=self.client_token,
                            exe_version=0x01000d00,
                            exe_hash=check_revision(
                                pack.seed_values,
                                pack.file_name
                            ),
                            number_of_cd_keys=2,
                            spawn_cd_key=0,
                            cd_keys=[
                                Container(
                                    key_length=16,
                                    cd_key_product=6,
                                    cd_key_public=clpub,
                                    hash=clhash,
                                ),
                                Container(
                                    key_length=16,
                                    cd_key_product=12,
                                    cd_key_public=lodpub,
                                    hash=lodhash,
                                ),
                            ],
                            exe_info=b"Game.exe 10/18/11 20:48:14 65536",
                            cd_key_owner=b"yoba",
                        )
                    )
                )

            elif pack.packet_id == "SID_AUTH_CHECK":
                if pack.result != 0:
                    logging.info("[bnet.py] Not zero result on \n{}".format(pack))
                    self.login_error(pack.packet_id, pack.result)
                else:
                    self.sock.sendall(
                        spacket.build(
                            Container(
                                packet_id="SID_LOGONRESPONSE2",
                                client_token=self.client_token,
                                server_token=self.server_token,
                                hash=sub_double_hash(
                                    self.client_token,
                                    self.server_token,
                                    self.hashpass
                                ),
                                username=self.username,
                            )
                        )
                    )

            elif pack.packet_id == "SID_LOGONRESPONSE2":
                if pack.result != 0:
                    logging.info("[bnet.py] Not zero result on \n{}".format(pack))
                    self.login_error(pack.packet_id, pack.result)
                else:
                    self.sock.sendall(
                        spacket.build(
                            Container(
                                packet_id="SID_ENTERCHAT",
                                username=self.username,
                                statstring=b"",
                            )
                        )
                    )
                    self.sock.sendall(
                        spacket.build(
                            Container(
                                packet_id="SID_GETCHANNELLIST",
                                product_id=b"PX2D",
                            )
                        )
                    )

            elif pack.packet_id == "SID_ENTERCHAT":
                self.sock.sendall(
                    spacket.build(
                        Container(
                            packet_id="SID_JOINCHANNEL",
                            unknown=5,
                            channel_name=b"Diablo II",
                        )
                    )
                )

            elif pack.packet_id == "SID_CHATEVENT":
                if packet.event_id in ("ID_USER", "ID_JOIN"):
                    text = str(packet.text, "ascii")
                    nickname = ""
                    if text.startswith("PX2D"):
                        text = text.split(",")
                        if len(text) > 2:
                            nickname = text[1]
                    self.nicknames[str(packet.username)] = nickname

                elif packet.event_id in ("ID_LEAVE",):
                    del self.nicknames[str(packet.username)]

                elif packet.event_id in ("ID_INFO",):
                    self.push_text(("blue", str(packet.text)))

                elif packet.event_id in ("ID_ERROR",):
                    self.push_text(("red", str(packet.text)))

                elif packet.event_id in ("ID_TALK",):
                    self.push_text(
                        ("nickname", self.nicknames[str(packet.username)] + "*" + str(packet.username)),
                        ": " + str(packet.text),
                    )

                else:
                    logging.info("[d-chat.py] unhandled chat event\n{}".format(packet))

                self.chat_event()

            else:
                logging.info("[bnet.py] unhandled packet\n{}".format(pack))
