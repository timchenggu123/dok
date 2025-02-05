class WaitingAnimation():
    def __init__(self, base=""):
        self.counter = 1
        self.base = base
        self.buffer = ""

    def update(self, s=""):
        self.clear()
        self.buffer = s + self.base + "."*self.counter 
        self.flush()
        if self.counter == 3:
            self.counter = 1
        else:
            self.counter += 1

    def clear(self):
        print(" "*len(self.buffer), end = "\r", flush=True)

    def flush(self):
        print(self.buffer, end = "\r", flush=True)

    def finish(self, s=""):
        print(self.buffer + s, flush=True)

