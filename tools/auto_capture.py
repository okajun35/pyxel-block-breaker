import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    env = os.environ.copy()
    env.setdefault("PYXEL_AUTORUN", "1")
    env.setdefault("PYXEL_AUTOCAP_FRAMES", "30,90,150,210")
    env.setdefault("PYXEL_AUTOEXIT_FRAME", "240")

    cmd = [sys.executable, str(ROOT / "block_breaker.py")]
    if shutil.which("xvfb-run"):
        cmd = ["xvfb-run", "-a", *cmd]

    subprocess.run(cmd, cwd=ROOT, env=env, check=True)

    tmp_dir = ROOT / "tmp"
    files = sorted(tmp_dir.glob("auto_*.png"))
    print("auto captures:")
    for f in files:
        print(f.as_posix())


if __name__ == "__main__":
    main()
