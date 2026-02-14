import json
from pathlib import Path


class MetricsStore:
    def __init__(self, path: Path):
        self.path = path

    def append(
        self,
        mode: str,
        protocol: str,
        time_sec: int,
        score: int,
        max_combo: int,
        damage: int,
        phase: int,
    ):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "mode": mode,
            "protocol": protocol,
            "time_sec": int(time_sec),
            "score": int(score),
            "max_combo": int(max_combo),
            "damage": int(damage),
            "phase": int(phase),
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")

    def read_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
        return rows

    def summary(self) -> dict:
        rows = self.read_all()
        mode_count: dict[str, int] = {}
        protocol_count: dict[str, int] = {}
        for row in rows:
            mode = row.get("mode", "unknown")
            protocol = row.get("protocol", "unknown")
            mode_count[mode] = mode_count.get(mode, 0) + 1
            protocol_count[protocol] = protocol_count.get(protocol, 0) + 1
        return {
            "runs": len(rows),
            "mode_count": mode_count,
            "protocol_count": protocol_count,
        }
