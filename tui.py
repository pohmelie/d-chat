import urwid
import logging


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

    def on_input(self, key):
        pass
