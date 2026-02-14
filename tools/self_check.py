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
    JP_FONT_SYSTEM_CANDIDATES,
    JP_SMALL_FONT_PATH,
    JP_FONT_SIZE,
    WIDTH,
)

def load_font_from_candidates(size: int):
    candidates = [JP_FONT_PATH, *JP_FONT_SYSTEM_CANDIDATES]
    for path in candidates:
        try:
            return pyxel.Font(path, size), f"ttf:{path}@{size}"
        except Exception:
            continue
    return pyxel.Font(JP_FONT_FALLBACK_PATH), f"bdf:{JP_FONT_FALLBACK_PATH}"


def load_small_font():
    try:
        return pyxel.Font(JP_SMALL_FONT_PATH), f"bdf:{JP_SMALL_FONT_PATH}"
    except Exception:
        return load_font_from_candidates(JP_FONT_SIZE)


def main():
    tmp = ROOT / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    font_main, font_main_name = load_font_from_candidates(JP_FONT_SIZE)
    font_small, font_small_name = load_small_font()
    t1 = time.perf_counter()

    img = pyxel.Image(WIDTH, HEIGHT)
    img.cls(1)
    img.rect(8, 28, 188, 96, 0)
    img.rectb(8, 28, 188, 96, 7)
    img.text(14, 36, "あそびかた", 10, font_main)
    img.text(14, 48, "1/2/3: むずかしさ", 7, font_small)
    img.text(14, 60, "TAB: モードきりかえ", 7, font_small)
    img.text(14, 72, "ひだり/みぎ: いどう", 7, font_small)
    img.text(14, 84, "W/S/M/F: アイテム", 7, font_small)
    img.text(14, 96, "SPACE: スタート", 10, font_small)
    img.text(14, 108, "C: がめん保存", 10, font_small)
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
