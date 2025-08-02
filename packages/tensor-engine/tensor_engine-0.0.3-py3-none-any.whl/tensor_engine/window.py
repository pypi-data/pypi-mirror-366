import sys, os, time
from object import Object
from pynput import keyboard

class Display:
    def __init__(self, size: tuple[int, int], fr: int=3):
        self.frames = 0
        self.fr = fr
        self.size = size
        self.pressed_keys = set()
        self.reset()
        self.clear()
        print("\033[2J\033[H\033[?25l", end='')
        self._start_key_listener()

    def clear(self):
        os.system('cls')

    def _start_key_listener(self):
        def on_press(key):
            try:
                self.pressed_keys.add(key.char.lower())
            except AttributeError:
                pass

        def on_release(key):
            try:
                self.pressed_keys.discard(key.char.lower())
            except AttributeError:
                pass

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.daemon = True
        listener.start()

    def check_key(self, key: str) -> bool:
        return key.lower() in self.pressed_keys

    def reset(self):
        self.display = []
        for x in range(self.size[1]):
            layer = []
            if x == 0 or x == self.size[1]-1:
                layer.extend(['#'] * self.size[0])
            else:
                layer.append('#')
                layer.extend([' '] * (self.size[0]-2))
                layer.append('#')
            self.display.append(layer)

    def draw(self, object: Object):
        render_data = object.render()
        for y in range(object.size[1]):
            for x in range(object.size[0]):
                try:
                    self.display[y+1+object.y][x+1+object.x] = render_data[y][x]
                except:
                    pass

    def __del__(self):
        print("\033[?25h", end='')

    def update(self):
        if self.frames >= self.fr:
            print("\033[H", end='')
            for layer in self.display:
                print(' '.join(layer), flush=True)
            self.reset()
            sys.stdout.flush()
            self.frames = 0
        self.frames += 1
        time.sleep(0.1/self.fr)