import bnet
import tui
import urwid
import logging
import sys
import time
import itertools
import collections


class Dchat():
    def __init__(self, host, port, account, password):
        self.account = account
        self.password = password
        self.channel = ""

        self.bnet = bnet.Bnet(host, port, self.login_error, self.chat_event)
        self.tui = tui.Tui()

        self.nicknames = {}
        self.navigation = {
            "ctrl up":lambda: self.tui.chat.up(),
            "ctrl down":lambda: self.tui.chat.down(),
            "page up":lambda: self.tui.chat.up(10),
            "page down":lambda: self.tui.chat.down(10),
            "ctrl home":lambda: self.tui.chat.home(),
            "ctrl end":lambda: self.tui.chat.end(),
        }

    def run(self):
        self.bnet.login(self.account, self.password)

        loop = urwid.MainLoop(
            self.tui.frame,
            palette=self.tui.palette,
            handle_mouse=False,
            unhandled_input=self.on_input
        )
        loop.watch_file(self.bnet.sock, self.bnet.on_packet)
        loop.run()

    def say(self):
        msg = self.tui.inpu.get_edit_text()
        self.tui.inpu.set_edit_text("")

        curr_view = self.views[self.view_index]

        if msg.starts_with("/w "):
            pass

        elif msg.starts_with("/"):
            pass

        else:
            pass

        self.bnet.say(msg)
        self.push(
            ("delimiter", "*"),
            ("nickname", self.account),
            ("delimiter", ": "),
            ("text", msg),
        )

    def on_input(self, key):
        #self.push(key)

        if key in self.navigation:
            self.navigation[key]()
            self.tui.chat.refresh()

        elif key == "enter":
            self.say()

        elif key == "ctrl x":
            raise urwid.ExitMainLoop()

        elif key == "ctrl w":
            self.tui.chat.switch()

    def push(self, *args, **kwargs):
        if kwargs.get("whisper", False):
            color = "whisper time"
        else:
            color = "time"
        self.tui.chat.push((color, time.strftime("[%H:%M:%S] ")), *args, **kwargs)

    def login_error(self, packet_id, retcode=None):
        if retcode is None:
            msg = "error on '{}'".format(packet_id)
        else:
            msg = "error on '{}' with retcode = {}".format(packet_id, retcode)

        self.push(("red", msg))
        self.tui.chat.refresh()

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
                ("nickname", nick_name),
                ("delimiter", "*"),
                ("nickname", acc_name),
                ("delimiter", ": "),
                ("text", str(packet.text, "utf-8")),
            )

        elif packet.event_id in ("ID_CHANNEL",):
            self.channel = str(packet.text, "utf-8")

        elif packet.event_id in ("ID_WHISPER",):
            acc_name = str(packet.username, "utf-8")
            nick_name = self.nicknames.get(acc_name, "")
            self.push(
                ("whisper nickname", nick_name),
                ("delimiter", "*"),
                ("whisper nickname", acc_name),
                ("delimiter", " -> "),
                ("whisper nickname", "*" + self.account),
                ("delimiter", ": "),
                ("whisper", str(packet.text, "utf-8")),
                whisper=True,
            )

        else:
            logging.info("[d-chat.py] unhandled chat event\n{}".format(packet))


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

    Dchat("rubattle.net", 6112, *sys.argv[1:3]).run()
