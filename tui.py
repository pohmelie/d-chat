import urwid
import logging


class ChatView():
    def __init__(self, max_size=1000):
        self.max_size = max_size
        self.shift = 0
        self.lines = ()

    def __getitem__(self, position):
        return self.lines[-position - self.shift - 1]

    def push(self, *objs):
        self.lines = (self.lines + objs)[-self.max_size:]
        if self.shift != 0:
            self.shift = self.shift + len(objs)

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

    def down(self, count=1):
        self.shift = max(0, self.shift - count)

    def home(self):
        self.shift = len(self.lines) - 1

    def end(self):
        self.shift = 0


class ChatWalker(urwid.ListWalker):
    def __init__(self, view):
        urwid.ListWalker.__init__(self)

        self.focus = 0
        self.view = view

    def set_view(self, view):
        self.view = view
        self.__getitem__ = self.view.__getitem__
        self.next_position = self.view.next_position
        self.prev_position = self.view.prev_position

    def refresh(self):
        urwid.ListWalker._modified(self)


class Tui():
    def __init__(self, view):
        self.chat = ChatWalker(view)
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

    def set_view(self, view):
        self.caht.set_view(view)
        self.inpu.set_
