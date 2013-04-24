import urwid
import time


class ChatWalker(urwid.ListWalker):
    def __init__(self, max_size=1000):
        urwid.ListWalker.__init__(self)

        self.max_size = max_size
        self.focus = 0

        self.shift = 0
        self.lines = ()

    def get_view(self):
        return (self.max_size, self.shift, self.lines)

    def set_view(self, view):
        self.max_size, self.shift, self.lines = view
        urwid.ListWalker._modified(self)

    def __getitem__(self, position):
        return self.lines[-position - self.shift - 1]

    def push(self, *objs):
        self.lines = (self.lines + objs)[-self.max_size:]
        if self.shift != 0:
            self.shift = self.shift + len(objs)
        else:
            urwid.ListWalker._modified(self)

    def next_position(self, position):
        if position <= 0:
            raise IndexError
        return position - 1

    def prev_position(self, position):
        if position >= len(self.lines) - self.shift:
            raise IndexError
        return position + 1

    def up(self, count=1):
        self.shift = max(0, min(len(self.lines) - 1, self.shift + count))
        urwid.ListWalker._modified(self)

    def down(self, count=1):
        self.shift = max(0, self.shift - count)
        urwid.ListWalker._modified(self)

    def home(self):
        self.shift = len(self.lines) - 1
        urwid.ListWalker._modified(self)

    def end(self):
        self.shift = 0
        urwid.ListWalker._modified(self)


class Tab():
    def __init__(self, desc="", view=None):
        self.desc = desc
        self.view = view


class Tui():
    def __init__(self):
        self.chat = ChatWalker()
        self.inpu = urwid.Edit(caption=("input", "> "), wrap="clip")

        self.chat_box = urwid.LineBox(urwid.ListBox(self.chat))
        self.frame = urwid.Frame(
            self.chat_box,
            footer=urwid.LineBox(self.inpu)
        )

        self.frame.set_focus_path(("footer",))

        self.palette = (
            ("time", "dark green", "default"),
            ("whisper", "light green", "default"),
            ("system", "light cyan", "default"),
            ("nickname", "white", "default"),
            ("input", "white", "default"),
            ("red", "light red", "default"),
            ("blue", "system"),
        )

        self.tabs = [Tab("main", self.chat.get_view())]
        self.current_tab = 0

        self.players_count = 0


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
            #self.login_error("yoba", 0)

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

if __name__ == "__main__":
    tui = Tui()
    loop = urwid.MainLoop(tui.frame, palette=tui.palette, handle_mouse=False, unhandled_input=tui.on_input)
    tui.chat_box.set_title("yoba")
    loop.run()
