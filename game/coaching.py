from game.run_report import RunReport


def suggest_next_actions(report: RunReport, recent_causes: list[str]) -> list[str]:
    tips: list[str] = []
    enemy_hits = sum(1 for c in recent_causes if c.startswith("enemy_reach"))
    ball_drops = sum(1 for c in recent_causes if c == "ball_drop")

    if enemy_hits >= 2:
        tips.append("敵が下段に来る前に優先撃破しよう")
    if ball_drops >= 1:
        tips.append("バー中央で受けてから角度を作ろう")
    if report.max_combo <= 2:
        tips.append("浅い角度でコンボ継続を意識しよう")
    if report.cleared_phase <= 2:
        tips.append("序盤はWかSを1つ取って安定化しよう")
    if not tips:
        tips.append("次は難易度かプロトコルを変えて試そう")
    return tips[:3]
