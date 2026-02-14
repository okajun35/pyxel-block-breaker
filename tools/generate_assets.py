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
    img.circ(3, 27, 3, 10)
    img.circb(3, 27, 3, 7)

    img.circ(11, 19, 3, 14)
    img.circb(11, 19, 3, 7)
    img.circ(11, 27, 3, 9)
    img.circb(11, 27, 3, 7)

    img.circ(19, 19, 3, 11)
    img.circb(19, 19, 3, 7)
    img.circ(19, 27, 3, 12)
    img.circb(19, 27, 3, 7)

    img.circ(27, 19, 3, 2)
    img.circb(27, 19, 3, 7)
    img.circ(27, 27, 3, 3)
    img.circb(27, 27, 3, 7)

    img.circ(38, 21, 5, 7)
    img.circb(38, 21, 5, 8)
    img.circ(54, 21, 5, 6)
    img.circb(54, 21, 5, 8)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path), 1)


def gen_panel(path: Path):
    img = pyxel.Image(196, 96)
    img.cls(0)
    img.rectb(0, 0, 196, 96, 7)
    img.rect(2, 2, 192, 92, 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path), 1)


def gen_bg(path: Path, variant: int):
    img = pyxel.Image(240, 180)
    base_col = [1, 5, 2, 0][(variant - 1) % 4]
    line_col = [5, 6, 11, 13][(variant - 1) % 4]
    star_col_a = [7, 10, 7, 6][(variant - 1) % 4]
    star_col_b = [6, 7, 14, 12][(variant - 1) % 4]
    img.cls(base_col)
    for x in range(0, 240, 24):
        img.line(x, 0, x + 60, 179, line_col)
    for y in range(6, 180, 24):
        img.pset((y * (11 + variant)) % 239, y, star_col_a)
        img.pset((y * (19 + variant * 2)) % 239, y // 2, star_col_b)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path), 1)


def main():
    gen_sheet(ASSETS / "sprites/sheet.png")
    gen_panel(ASSETS / "ui/panel_start.png")
    for idx in range(1, 5):
        gen_bg(ASSETS / f"backgrounds/starfield_{idx:02d}.png", idx)
    print("generated assets:")
    print(ASSETS / "sprites/sheet.png")
    print(ASSETS / "ui/panel_start.png")
    for idx in range(1, 5):
        print(ASSETS / f"backgrounds/starfield_{idx:02d}.png")


if __name__ == "__main__":
    main()
