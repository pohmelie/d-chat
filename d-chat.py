import tui
import urwid
import logging
import sys
import time


class Dchat(tui.Tui):
    def __init__(self, host, port):
        tui.Tui.__init__(self, host, port)

    def on_input(self, key):
        if key == "ctrl x":
            raise urwid.ExitMainLoop()

        elif key == "ctrl up":
            self.chat.up()

        elif key == "ctrl down":
            self.chat.down()

        elif key == "page up":
            self.chat.up(10)

        elif key == "page down":
            self.chat.down(10)

        elif key == "ctrl home":
            self.chat.home()

        elif key == "ctrl end":
            self.chat.end()

        elif key == "enter":
            pass

    def get_time(self):
        return ("time", time.strftime("[%H:%M:%S]"))

    def login_error(self, packet_id, retcode):
        self.chat.push(
            urwid.Text([
                self.get_time(),
                " ",
                ("red", "error on '{}' with retcode = {}".format(packet_id, retcode))
            ])
        )

    def chat_event(self, packet):
        logging.info("[d-chat.py] Chat event \n{}".format(packet))
        self.chat.push(
            urwid.Text([
                self.get_time(),
                " ",
                packet.event_id,
                " ",
                "[{}]".format(packet.username)
            ])
        )
        return

        if packet.event_id in ("ID_USER", "ID_JOIN"):
            self.players_count = self.players_count + 1

        elif packet.event_id in ("ID_LEAVE"):
            self.players_count = self.players_count - 1


if len(sys.argv) < 3:
    print("Usage: d-chat.py nickname password")
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
