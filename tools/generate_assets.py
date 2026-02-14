from pathlib import Path

import pyxel

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def gen_sheet(path: Path):
    img = pyxel.Image(64, 32)
    img.cls(1)
    img.rect(0, 0, 18, 6, 13)
    img.rectb(0, 0, 18, 6, 7)
    img.rect(18, 0, 18, 6, 2)
    img.rectb(18, 0, 18, 6, 7)
    img.rect(36, 0, 18, 6, 3)
    img.rectb(36, 0, 18, 6, 7)

    img.rect(0, 8, 6, 6, 9)
    img.rectb(0, 8, 6, 6, 7)
    img.rect(6, 8, 6, 6, 11)
    img.rectb(6, 8, 6, 6, 7)
    img.rect(12, 8, 6, 6, 14)
    img.rectb(12, 8, 6, 6, 7)
    img.rect(18, 8, 6, 6, 8)
    img.rectb(18, 8, 6, 6, 7)

    img.circ(3, 19, 3, 8)
    img.circb(3, 19, 3, 7)
    img.circ(11, 19, 3, 14)
    img.circb(11, 19, 3, 7)
    img.circ(19, 19, 3, 11)
    img.circb(19, 19, 3, 7)
    img.circ(27, 19, 3, 2)
    img.circb(27, 19, 3, 7)
    img.circ(38, 21, 5, 7)
    img.circb(38, 21, 5, 8)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path), 1)


def gen_panel(path: Path):
    img = pyxel.Image(196, 96)
    img.cls(0)
    img.rectb(0, 0, 196, 96, 7)
    img.rect(2, 2, 192, 92, 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path), 1)


def gen_bg(path: Path):
    img = pyxel.Image(240, 180)
    img.cls(1)
    for x in range(0, 240, 24):
        img.line(x, 0, x + 60, 179, 5)
    for y in range(6, 180, 24):
        img.pset((y * 13) % 239, y, 7)
        img.pset((y * 31) % 239, y // 2, 6)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path), 1)


def main():
    gen_sheet(ASSETS / "sprites/sheet.png")
    gen_panel(ASSETS / "ui/panel_start.png")
    gen_bg(ASSETS / "backgrounds/starfield.png")
    print("generated assets:")
    print(ASSETS / "sprites/sheet.png")
    print(ASSETS / "ui/panel_start.png")
    print(ASSETS / "backgrounds/starfield.png")


if __name__ == "__main__":
    main()
