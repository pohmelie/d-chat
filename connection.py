import socket
import asyncore
import collections


class Connection(asyncore.dispatcher):
    def __init__(self, callback):
        asyncore.dispatcher.__init__(self)

        self.callback = callback
        self.qsend = collections.deque()

    def push(self, x):
        self.qsend.appendleft(x)

    def writable(self):
        return len(self.qsend) != 0

    def handle_read(self):
        self.callback(self.recv(2 ** 16))

    def handle_write(self):
        while len(self.qsend) != 0:
            self.send(self.qsend.pop())

if __name__ == "__main__":
    import time
    import threading
    con = Connection(print)
    con.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    con.connect(("google.ru", 80))
    t = threading.Thread(target=asyncore.loop, args=(0.1,))
    t.daemon = True
    t.start()
    for i in range(5):
        print(t.is_alive())
        time.sleep(5)
    con.close()
    while True:
        print(t.is_alive())
        time.sleep(5)
