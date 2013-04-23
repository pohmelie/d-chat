import urwid
import time


class Tui():
    def __init__(self):
        self.messages = []

        self.chat = urwid.Text("")
        self.inpu = urwid.Edit(caption=("input", "> "), wrap="clip")

        self.chat_box = urwid.LineBox(urwid.Filler(self.chat, "bottom"))
        self.frame = urwid.Frame(self.chat_box, footer=urwid.LineBox(self.inpu))

        self.palette = (
            ("time", "dark green", "default"),
            ("whisper", "light green", "default"),
            ("system", "light cyan", "default"),
            ("nickname", "white", "default"),
            ("input", "white", "default"),
            ("red", "light red", "default"),
            ("blue", "system"),
        )

        self.rcode = 0

    def on_input(self, key):
        if key == "ctrl x":
            raise urwid.ExitMainLoop()
        elif key == "enter":
            self.login_error("yoba", self.rcode)
            self.rcode = self.rcode + 1

    def get_time(self):
        return ("time", time.strftime("[%H:%M:%S]"))

    def login_error(self, packet_id, retcode):
        self.messages = self.messages + [
            "\n",
            self.get_time(),
            " ",
            ("red", "'{}' retcode = {}".format(packet_id, retcode))
        ]
        self.chat.set_text(self.messages)

    def chat_event(self, packet):
        pass


if __name__ == "__main__":
    tui = Tui()
    loop = urwid.MainLoop(tui.frame, palette=tui.palette, unhandled_input=tui.on_input)
    tui.chat_box.set_title("yoba")
    tui.frame.set_focus_path(("footer",))
    loop.run()
