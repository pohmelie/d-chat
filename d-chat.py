import bnet
import tui
import urwid
import logging
import sys
import time


class Dchat(bnet.Bnet, tui.Tui):
    def __init__(self, host, port):
        bnet.Bnet.__init__(self, host, port)
        tui.Tui.__init__(self)

        self.nicknames = {}
        self.navigation = {
            "ctrl up":self.chat.up,
            "ctrl down":self.chat.down,
            "page up":lambda: self.chat.up(10),
            "page down":lambda: self.chat.down(10),
            "ctrl home":self.chat.home,
            "ctrl end":self.chat.end,
        }

    def on_input(self, key):
        if key in self.navigation:
            self.navigation[key]()

        elif key == "ctrl x":
            raise urwid.ExitMainLoop()

        elif key == "enter":
            pass

    def get_time(self):
        return ("time", time.strftime("[%H:%M:%S]"))

    def push_text(self, *txt):
        self.chat.push(urwid.Text([self.get_time(), " "] + list(txt)))

    def login_error(self, packet_id, retcode=None):
        if retcode is None:
            msg = "error on '{}'".format(packet_id)
        else:
            msg = "error on '{}' with retcode = {}".format(packet_id, retcode)
        self.push_text(("red", msg))

    def chat_event(self, packet):
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

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: d-chat.py account password\n")
        exit()

    logging.basicConfig(
        filename="d-chat.log",
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="[%H:%M:%S]",
    )

    d = Dchat("rubattle.net", 6112)
    d.login(*sys.argv[1:3])
    loop = urwid.MainLoop(d.frame, palette=d.palette, handle_mouse=False, unhandled_input=d.on_input)
    loop.watch_file(d.sock, d.on_packet)
    loop.run()
