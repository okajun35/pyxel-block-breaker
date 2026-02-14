def stage_music_pattern(stage: int) -> list[int]:
    idx = ((max(1, stage) - 1) % 4) + 1
    if idx == 1:
        return [0, 1]
    if idx == 2:
        return [8, 1]
    if idx == 3:
        return [8, 9]
    return [10, 11]
