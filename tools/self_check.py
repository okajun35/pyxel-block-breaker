import time
from pathlib import Path
import sys
import shutil
import os

import pyxel

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from game.constants import (
    HEIGHT,
    JP_FONT_FALLBACK_PATH,
    JP_FONT_PATH,
    JP_SMALL_FONT_PATH,
    JP_FONT_SIZE,
    WIDTH,
)


def load_font(path: str, size: int):
    try:
        return pyxel.Font(path, size), f"ttf:{path}@{size}"
    except Exception:
        return pyxel.Font(JP_FONT_FALLBACK_PATH), f"bdf:{JP_FONT_FALLBACK_PATH}"


def load_small_font():
    try:
        return pyxel.Font(JP_SMALL_FONT_PATH), f"bdf:{JP_SMALL_FONT_PATH}"
    except Exception:
        return load_font(JP_FONT_PATH, JP_FONT_SIZE)


def main():
    tmp = ROOT / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    font_main, font_main_name = load_font(JP_FONT_PATH, JP_FONT_SIZE)
    font_small, font_small_name = load_small_font()
    t1 = time.perf_counter()

    img = pyxel.Image(WIDTH, HEIGHT)
    img.cls(1)
    img.rect(8, 28, 144, 72, 0)
    img.rectb(8, 28, 144, 72, 7)
    img.text(14, 36, "あそびかた", 10, font_main)
    img.text(14, 48, "ひだり/みぎ いどう", 7, font_small)
    img.text(14, 58, "ぜんぶこわして クリア", 7, font_small)
    img.text(14, 68, "W:バー  S:スロー", 7, font_small)
    img.text(14, 78, "M:+たま  F:はやい(2~)", 7, font_small)
    img.text(14, 90, "SPACE:スタート C:保存", 10, font_small)
    img.save(str(tmp / "jp_selfcheck.png"), 1)

    ti0 = time.perf_counter()
    pyxel.init(64, 64, title="self-check")
    pyxel.cls(1)
    pyxel.text(4, 4, "C", 7)
    raw_name = ".selfcheck_capture.png"
    pyxel.screen.save(raw_name, 1)
    shutil.move(raw_name, tmp / "jp.png")
    ti1 = time.perf_counter()

    report = (
        f"font_main={font_main_name}\n"
        f"font_small={font_small_name}\n"
        f"font_load={t1 - t0:.4f}s\n"
        f"init_plus_save={ti1 - ti0:.4f}s\n"
        f"selfcheck_image={tmp / 'jp_selfcheck.png'}\n"
        f"screen_capture={tmp / 'jp.png'}\n"
    )
    (tmp / "self_check.txt").write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()
