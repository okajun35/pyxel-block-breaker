import os
import sys
import time
from pathlib import Path

import pyxel

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from game.constants import HEIGHT, JP_FONT_PATH, JP_FONT_SIZE, WIDTH


def main():
    t0 = time.perf_counter()
    pyxel.init(WIDTH, HEIGHT, title="startup-measure")
    t1 = time.perf_counter()

    tf0 = time.perf_counter()
    pyxel.Font(JP_FONT_PATH, JP_FONT_SIZE)
    tf1 = time.perf_counter()

    lines = [
        f"pyxel.init={t1 - t0:.4f}s",
        f"font_load={tf1 - tf0:.4f}s",
    ]
    out = ROOT / "tmp" / "startup_measure.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
