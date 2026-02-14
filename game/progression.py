import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProgressionState:
    core_shards: int = 0
    life_upgrade_level: int = 0


class ProgressionStore:
    MAX_LIFE_UPGRADE = 3
    LIFE_UPGRADE_COST = 10

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
        )

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "core_shards": self.state.core_shards,
            "life_upgrade_level": self.state.life_upgrade_level,
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
