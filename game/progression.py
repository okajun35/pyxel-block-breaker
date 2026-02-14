import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProgressionState:
    core_shards: int = 0
    life_upgrade_level: int = 0
    core_gain_upgrade_level: int = 0
    paddle_upgrade_level: int = 0
    tutorial_seen: bool = False


class ProgressionStore:
    MAX_LIFE_UPGRADE = 3
    LIFE_UPGRADE_COST = 10
    MAX_CORE_GAIN_UPGRADE = 3
    CORE_GAIN_UPGRADE_COST = 12
    MAX_PADDLE_UPGRADE = 3
    PADDLE_UPGRADE_COST = 10

    def __init__(self, path: Path):
        self.path = path
        self.state = ProgressionState()
        self.load()

    def load(self):
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return
        self.state = ProgressionState(
            core_shards=max(0, int(data.get("core_shards", 0))),
            life_upgrade_level=max(0, min(self.MAX_LIFE_UPGRADE, int(data.get("life_upgrade_level", 0)))),
            core_gain_upgrade_level=max(
                0, min(self.MAX_CORE_GAIN_UPGRADE, int(data.get("core_gain_upgrade_level", 0)))
            ),
            paddle_upgrade_level=max(
                0, min(self.MAX_PADDLE_UPGRADE, int(data.get("paddle_upgrade_level", 0)))
            ),
            tutorial_seen=bool(data.get("tutorial_seen", False)),
        )

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "core_shards": self.state.core_shards,
            "life_upgrade_level": self.state.life_upgrade_level,
            "core_gain_upgrade_level": self.state.core_gain_upgrade_level,
            "paddle_upgrade_level": self.state.paddle_upgrade_level,
            "tutorial_seen": self.state.tutorial_seen,
        }
        self.path.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")

    def add_core(self, amount: int):
        if amount <= 0:
            return
        self.state.core_shards += amount
        self.save()

    def try_upgrade_life(self) -> bool:
        if self.state.life_upgrade_level >= self.MAX_LIFE_UPGRADE:
            return False
        if self.state.core_shards < self.LIFE_UPGRADE_COST:
            return False
        self.state.core_shards -= self.LIFE_UPGRADE_COST
        self.state.life_upgrade_level += 1
        self.save()
        return True

    def try_upgrade_core_gain(self) -> bool:
        if self.state.core_gain_upgrade_level >= self.MAX_CORE_GAIN_UPGRADE:
            return False
        if self.state.core_shards < self.CORE_GAIN_UPGRADE_COST:
            return False
        self.state.core_shards -= self.CORE_GAIN_UPGRADE_COST
        self.state.core_gain_upgrade_level += 1
        self.save()
        return True

    def try_upgrade_paddle(self) -> bool:
        if self.state.paddle_upgrade_level >= self.MAX_PADDLE_UPGRADE:
            return False
        if self.state.core_shards < self.PADDLE_UPGRADE_COST:
            return False
        self.state.core_shards -= self.PADDLE_UPGRADE_COST
        self.state.paddle_upgrade_level += 1
        self.save()
        return True

    def mark_tutorial_seen(self):
        if self.state.tutorial_seen:
            return
        self.state.tutorial_seen = True
        self.save()
