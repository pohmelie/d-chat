import urwid


class ChatView():
    def __init__(self, title_format="", max_size=1000):
        self.max_size = max_size
        self.shift = 0
        self.lines = ()
        self.title_format = title_format
        self.title = "Testing..."

    def __getitem__(self, position):
        return self.lines[-position - self.shift - 1]

    def set_title(self, *args):
        self.title = self.title_format.format(*args)

    def push(self, *objs):
        self.lines = (self.lines + (urwid.Text(list(objs)),))[-self.max_size:]
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
    def __init__(self):
        urwid.ListWalker.__init__(self)
        self.focus = 0
        self.view = None

    def __getitem__(self, position):
        if self.view:
            return self.view[position]

    def set_view(self, view):
        self.view = view
        self.next_position = view.next_position
        self.prev_position = view.prev_position

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
            ("time", urwid.LIGHT_BLUE, urwid.BLACK),
            ("system", urwid.LIGHT_CYAN, urwid.BLACK),
            ("nickname", urwid.DARK_GREEN, urwid.BLACK),
            ("text", urwid.WHITE, urwid.BLACK),
            ("input", urwid.WHITE, urwid.BLACK),
            ("red", urwid.LIGHT_RED, urwid.BLACK),
            ("delimiter", urwid.BROWN, urwid.BLACK),
        )

    def set_view(self, view):
        self.view = view
        self.chat.set_view(view)
        self.refresh()

    def refresh(self):
        self.chat_box.set_title(self.view.title)
        self.chat.refresh()
