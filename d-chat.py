import bnet
import tui
import urwid
import logging
import sys
import time
import itertools


class Dchat():
    def __init__(self, host, port):
        self.main_view = tui.ChatView()
        self.views = [self.main_view]
        self.view_index = 0

        self.bnet = bnet.Bnet(host, port, self.login_error, self.chat_event)
        self.tui = tui.Tui()

        self.tui.set_view(self.main_view)

        self.nicknames = {}
        self.navigation = {
            "ctrl up":lambda: self.views[self.view_index].up(),
            "ctrl down":lambda: self.views[self.view_index].down(),
            "page up":lambda: self.views[self.view_index].up(10),
            "page down":lambda: self.views[self.view_index].down(10),
            "ctrl home":lambda: self.views[self.view_index].home(),
            "ctrl end":lambda: self.views[self.view_index].end(),
        }

    def on_input(self, key):
        if key in self.navigation:
            self.navigation[key]()
            self.tui.refresh()

        elif key == "ctrl x":
            raise urwid.ExitMainLoop()

        elif key == "enter":
            pass

        elif key == "ctrl tab":
            self.view_index = (self.view_index + 1) % len(self.views)
            self.tui.set_view(self.views[self.view_index])

        elif key == "ctrl shift tab":
            self.view_index = (self.view_index - 1) % len(self.views)
            self.tui.set_view(self.views[self.view_index])

        elif key == "ctrl w":
            if self.views[self.viewindex] is not self.main_view:
                del self.views[self.viewindex]
                self.view_index = self.view_index % len(self.views)
                self.tui.set_view(self.views[self.view_index])

    def push(self, *args):
        self.views[self.view_index].push(self.get_time(), *args)
        self.tui.refresh()

    def get_time(self):
        return ("time", time.strftime("[%H:%M:%S] "))

    def login_error(self, packet_id, retcode=None):
        if retcode is None:
            msg = "error on '{}'".format(packet_id)
        else:
            msg = "error on '{}' with retcode = {}".format(packet_id, retcode)

        self.push(("red", msg))
        if self.views[self.view_index] is self.main_view:
            self.tui.refresh()

    def chat_event(self, packet):
        if packet.event_id in ("ID_USER", "ID_JOIN", "ID_USERFLAGS"):
            text = "".join(map(chr, itertools.takewhile(lambda ch: ch < 128, packet.text)))
            nickname = ""
            if text.startswith("PX2D"):
                text = text.split(",")
                if len(text) >= 2:
                    nickname = text[1]
            self.nicknames[str(packet.username, "utf-8")] = nickname

        elif packet.event_id in ("ID_LEAVE",):
            uname = str(packet.username, "utf-8")
            if uname in self.nicknames:
                del self.nicknames[uname]

        elif packet.event_id in ("ID_INFO",):
            self.push(("system", str(packet.text, "utf-8")))

        elif packet.event_id in ("ID_ERROR",):
            self.push(("red", str(packet.text, "utf-8")))

        elif packet.event_id in ("ID_TALK", "ID_EMOTE"):
            acc_name = str(packet.username, "utf-8")
            nick_name = self.nicknames.get(acc_name, "")
            self.push(
                ("nickname", acc_name),
                ("delimiter", "*"),
                ("nickname", nick_name),
                ("delimiter", ": "),
                ("text", str(packet.text, "utf-8")),
            )

        else:
            logging.info("[d-chat.py] unhandled chat event\n{}".format(packet))

        self.tui.refresh()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: d-chat.py account password\n")
        exit()

    logging.basicConfig(
        filename="d-chat.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="[%H:%M:%S]",
    )

    d = Dchat("rubattle.net", 6112)
    d.bnet.login(*sys.argv[1:3])
    loop = urwid.MainLoop(d.tui.frame, palette=d.tui.palette, handle_mouse=False, unhandled_input=d.on_input)
    loop.watch_file(d.bnet.sock, d.bnet.on_packet)
    loop.run()
