from game.run_report import RunReport


def suggest_next_actions(report: RunReport, recent_causes: list[str]) -> list[str]:
    tips: list[str] = []
    enemy_hits = sum(1 for c in recent_causes if c.startswith("enemy_reach"))
    ball_drops = sum(1 for c in recent_causes if c == "ball_drop")

    if enemy_hits >= 2:
        tips.append("てきをさきにたいおう")
    if ball_drops >= 1:
        tips.append("まんなかうけをいしき")
    if report.max_combo <= 2:
        tips.append("かくとてこんほいし")
    if report.cleared_phase <= 2:
        tips.append("しよはんはW/Sゆうせん")
    if not tips:
        tips.append("せつていをかえてちようせん")
    return tips[:3]
