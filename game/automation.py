from dataclasses import dataclass
from typing import Mapping


def parse_frames(value: str) -> list[int]:
    if not value:
        return []
    out: list[int] = []
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            n = int(chunk)
        except ValueError:
            continue
        if n >= 0:
            out.append(n)
    return sorted(set(out))


@dataclass(frozen=True)
class AutoRunConfig:
    enabled: bool
    capture_frames: list[int]
    exit_frame: int

    @staticmethod
    def from_env(env: Mapping[str, str]) -> "AutoRunConfig":
        enabled = env.get("PYXEL_AUTORUN", "0") == "1"
        capture_frames = parse_frames(env.get("PYXEL_AUTOCAP_FRAMES", ""))
        try:
            exit_frame = int(env.get("PYXEL_AUTOEXIT_FRAME", "0"))
        except ValueError:
            exit_frame = 0
        if exit_frame < 0:
            exit_frame = 0
        return AutoRunConfig(
            enabled=enabled,
            capture_frames=capture_frames,
            exit_frame=exit_frame,
        )
