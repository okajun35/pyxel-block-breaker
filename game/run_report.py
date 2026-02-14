from dataclasses import dataclass


@dataclass(frozen=True)
class RunReport:
    time_sec: int
    max_combo: int
    damage_taken: int
    cleared_phase: int
    score: int


def build_run_report(
    elapsed_frames: int,
    max_combo: int,
    damage_taken: int,
    cleared_phase: int,
    score: int,
) -> RunReport:
    return RunReport(
        time_sec=max(0, elapsed_frames // 60),
        max_combo=max(0, max_combo),
        damage_taken=max(0, damage_taken),
        cleared_phase=max(1, cleared_phase),
        score=max(0, score),
    )
