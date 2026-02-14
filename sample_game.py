import pyxel


class App:
    def __init__(self):
        pyxel.init(160, 120, title="Pyxel WSL Test")
        self.x = 80
        self.y = 60
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= 2
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += 2
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= 2
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += 2
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw(self):
        pyxel.cls(1)
        pyxel.text(6, 6, "Arrow keys: move  Q: quit", 7)
        pyxel.circ(self.x, self.y, 6, 10)


App()
