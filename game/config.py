from dataclasses import dataclass
import csv

from game.constants import ROOT_DIR
from game.enums import DifficultyMode, EnemyType, ItemType, ProtocolType


@dataclass(frozen=True)
class DifficultyProfile:
    mode: DifficultyMode
    display_name: str
    base_lives: int
    enemy_hp_mul: float
    enemy_damage_mul: float
    drop_rate_mul: float
    score_mul: float
    revive_count: int
    early_guard_seconds: int


@dataclass(frozen=True)
class ProtocolProfile:
    protocol: ProtocolType
    display_name: str
    item_spawn_mul: float
    fusion_drop_mul: float
    reflect_window_ms: int
    paddle_aim_assist_deg: int
    enemy_hp_mul: float
    combo_score_mul: float
    base_score_mul: float


@dataclass(frozen=True)
class RunPhase:
    phase_id: int
    time_start_sec: int
    time_end_sec: int
    label: str
    enemy_density_mul: float
    elite_spawn_rate: float
    shop_slot_count: int
    event_weight_risk: float
    event_weight_reward: float
    boss_type: str


@dataclass(frozen=True)
class ItemEffectProfile:
    item_id: ItemType
    display_name: str
    max_level: int
    base_duration_sec: int
    same_item_bonus_sec: int
    lvl2_bonus: str
    lvl3_bonus: str
    stage_min: int


@dataclass(frozen=True)
class EnemyProfile:
    enemy_id: EnemyType
    base_hp: int
    base_speed: float
    collision_damage: int
    phase_hp_gain_pct: float
    phase_speed_gain_pct: float
    hard_mode_extra_hp_pct: float
    hard_mode_extra_speed_pct: float


class BalanceConfig:
    def __init__(self):
        self.difficulty_profiles = self._load_difficulty_profiles()
        self.protocol_profiles = self._load_protocol_profiles()
        self.run_phases = self._load_run_phases()
        self.item_effect_profiles = self._load_item_effect_profiles()
        self.enemy_profiles = self._load_enemy_profiles()

    def _load_difficulty_profiles(self) -> dict[DifficultyMode, DifficultyProfile]:
        path = ROOT_DIR / "docs/tables/difficulty_modes.csv"
        profiles: dict[DifficultyMode, DifficultyProfile] = {}
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                mode = DifficultyMode(row["mode"])
                profiles[mode] = DifficultyProfile(
                    mode=mode,
                    display_name=row["display_name"],
                    base_lives=int(row["base_lives"]),
                    enemy_hp_mul=float(row["enemy_hp_mul"]),
                    enemy_damage_mul=float(row["enemy_damage_mul"]),
                    drop_rate_mul=float(row["drop_rate_mul"]),
                    score_mul=float(row["score_mul"]),
                    revive_count=int(row["revive_count"]),
                    early_guard_seconds=int(row["early_guard_seconds"]),
                )
        return profiles

    def _load_protocol_profiles(self) -> dict[ProtocolType, ProtocolProfile]:
        path = ROOT_DIR / "docs/tables/protocol_profiles.csv"
        profiles: dict[ProtocolType, ProtocolProfile] = {}
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                protocol = ProtocolType(row["protocol"])
                profiles[protocol] = ProtocolProfile(
                    protocol=protocol,
                    display_name=row["display_name"],
                    item_spawn_mul=float(row["item_spawn_mul"]),
                    fusion_drop_mul=float(row["fusion_drop_mul"]),
                    reflect_window_ms=int(row["reflect_window_ms"]),
                    paddle_aim_assist_deg=int(row["paddle_aim_assist_deg"]),
                    enemy_hp_mul=float(row["enemy_hp_mul"]),
                    combo_score_mul=float(row["combo_score_mul"]),
                    base_score_mul=float(row["base_score_mul"]),
                )
        return profiles

    def _load_run_phases(self) -> list[RunPhase]:
        path = ROOT_DIR / "docs/tables/run_phases.csv"
        phases: list[RunPhase] = []
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                phases.append(
                    RunPhase(
                        phase_id=int(row["phase_id"]),
                        time_start_sec=int(row["time_start_sec"]),
                        time_end_sec=int(row["time_end_sec"]),
                        label=row["label"],
                        enemy_density_mul=float(row["enemy_density_mul"]),
                        elite_spawn_rate=float(row["elite_spawn_rate"]),
                        shop_slot_count=int(row["shop_slot_count"]),
                        event_weight_risk=float(row["event_weight_risk"]),
                        event_weight_reward=float(row["event_weight_reward"]),
                        boss_type=row["boss_type"],
                    )
                )
        return phases

    def _load_item_effect_profiles(self) -> dict[ItemType, ItemEffectProfile]:
        path = ROOT_DIR / "docs/tables/item_effects.csv"
        profiles: dict[ItemType, ItemEffectProfile] = {}
        item_map = {
            "W": ItemType.WIDE,
            "S": ItemType.SLOW,
            "M": ItemType.MULTI,
            "F": ItemType.FAST,
        }
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                item_type = item_map[row["item_id"]]
                profiles[item_type] = ItemEffectProfile(
                    item_id=item_type,
                    display_name=row["display_name"],
                    max_level=int(row["max_level"]),
                    base_duration_sec=int(row["base_duration_sec"]),
                    same_item_bonus_sec=int(row["same_item_bonus_sec"]),
                    lvl2_bonus=row["lvl2_bonus"],
                    lvl3_bonus=row["lvl3_bonus"],
                    stage_min=int(row["stage_min"]),
                )
        return profiles

    def _load_enemy_profiles(self) -> dict[EnemyType, EnemyProfile]:
        path = ROOT_DIR / "docs/tables/enemy_scaling.csv"
        profiles: dict[EnemyType, EnemyProfile] = {}
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                enemy_type = EnemyType(row["enemy_id"])
                profiles[enemy_type] = EnemyProfile(
                    enemy_id=enemy_type,
                    base_hp=int(row["base_hp"]),
                    base_speed=float(row["base_speed"]),
                    collision_damage=int(row["collision_damage"]),
                    phase_hp_gain_pct=float(row["phase_hp_gain_pct"]),
                    phase_speed_gain_pct=float(row["phase_speed_gain_pct"]),
                    hard_mode_extra_hp_pct=float(row["hard_mode_extra_hp_pct"]),
                    hard_mode_extra_speed_pct=float(row["hard_mode_extra_speed_pct"]),
                )
        return profiles

    def get_difficulty(self, mode: DifficultyMode) -> DifficultyProfile:
        return self.difficulty_profiles[mode]

    def get_protocol(self, protocol: ProtocolType) -> ProtocolProfile:
        return self.protocol_profiles[protocol]

    def get_phase_by_elapsed_sec(self, elapsed_sec: int) -> RunPhase:
        for phase in self.run_phases:
            if phase.time_start_sec <= elapsed_sec < phase.time_end_sec:
                return phase
        return self.run_phases[-1]
