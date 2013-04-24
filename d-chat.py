import tui
import bnet
import urwid


t = tui.Tui()

b = bnet.Bnet(t.login_error, t.chat_event)
b.login("pohmelie9", "chat")

loop = urwid.MainLoop(t.frame, palette=t.palette, handle_mouse=False, unhandled_input=t.on_input)
loop.watch_file(b.sock, b.onpacket)

loop.run()
