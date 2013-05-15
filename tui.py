import time
import urwid
import collections


class ChatWalker(urwid.ListWalker):
    def __init__(self):
        urwid.ListWalker.__init__(self)
        self.focus = 0
        self.shift = 0
        self.all_messages = collections.deque(maxlen=10000)
        self.whisper_messages = collections.deque(maxlen=1000)
        self.lines = self.all_messages

        self.logger_all = open("d-chat-all.log", "a")
        self.logger_whisper = open("d-chat-whisper.log", "a")

    def log(self, logger, elements):
        s = ""
        for el in elements:
            if isinstance(el, tuple):
                el = el[1]
            s = s + el

        logger.write(time.strftime("[%Y.%m.%d]") + s + "\n")
        logger.flush()

    def __getitem__(self, position):
        return self.lines[position + self.shift]

    def push(self, *args, **kwargs):
        widget = urwid.Text(list(args))
        whisper = kwargs.get("whisper", False)

        if whisper:
            self.whisper_messages.appendleft(widget)
            self.log(self.logger_whisper, args)

        self.all_messages.appendleft(widget)
        self.log(self.logger_all, args)

        if (whisper or self.lines is self.all_messages) and self.shift != 0:
            self.up()

        self.refresh()

    def switch(self):
        if self.lines is self.all_messages:
            self.lines = self.whisper_messages
        else:
            self.lines = self.all_messages

        self.shift = 0
        self.refresh()

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

    def refresh(self):
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
            ("time", urwid.LIGHT_BLUE, urwid.DEFAULT),
            ("whisper time", urwid.LIGHT_GREEN, urwid.DEFAULT),
            ("whisper", urwid.LIGHT_GREEN, urwid.DEFAULT),
            ("system", urwid.LIGHT_CYAN, urwid.DEFAULT),
            ("nickname", urwid.LIGHT_GRAY, urwid.DEFAULT),
            ("whisper nickname", urwid.LIGHT_GREEN, urwid.DEFAULT),
            ("text", urwid.WHITE, urwid.DEFAULT),
            ("input", urwid.WHITE, urwid.DEFAULT),
            ("red", urwid.LIGHT_RED, urwid.DEFAULT),
            ("delimiter", urwid.BROWN, urwid.DEFAULT),
            ("autocomplete", urwid.DARK_GRAY, urwid.DEFAULT),
        )
