# AGENTS.md

## UI Layout Rules (Must Follow)

When modifying this project, always apply these layout rules:

1. Use safe area:
   - Keep a minimum margin of 8px from all screen edges.
2. Separate layers by state:
   - `WAITING_START`: prioritize overlay panel, hide non-essential HUD.
   - `PLAYING`: show gameplay HUD only.
3. Avoid overlap:
   - HUD text must not overlap the block field or start panel.
   - If overlap is possible, move HUD first, not gameplay entities.
4. Use layout helpers:
   - Do not hardcode ad-hoc coordinates in draw code.
   - Centralize placement via layout constants/helpers.
5. Keep text density low:
   - Max 1 line of controls in top area during gameplay.
   - Start panel should use short lines and fixed line spacing.

## Development Flow

- Prefer incremental changes with tests.
- Commit in small, meaningful steps.
- Keep features playable at each commit.
