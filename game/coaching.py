from game.run_report import RunReport


def suggest_next_actions(report: RunReport, recent_causes: list[str]) -> list[str]:
    tips: list[str] = []
    enemy_hits = sum(1 for c in recent_causes if c.startswith("enemy_reach"))
    ball_drops = sum(1 for c in recent_causes if c == "ball_drop")

    if enemy_hits >= 2:
        tips.append("敵を先に処理")
    if ball_drops >= 1:
        tips.append("中央受けを意識")
    if report.max_combo <= 2:
        tips.append("角度でコンボ維持")
    if report.cleared_phase <= 2:
        tips.append("序盤はW/S優先")
    if not tips:
        tips.append("設定を変えて挑戦")
    return tips[:3]
