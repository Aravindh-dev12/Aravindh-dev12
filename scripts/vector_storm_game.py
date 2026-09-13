#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import quote

STATE = Path("game/vector_storm_state.json")
README = Path("README.md")
MSG = Path(".game_message")
COLS, ROWS = 9, 5
START = "<!-- VECTOR_STORM_GAME_START -->"
END = "<!-- VECTOR_STORM_GAME_END -->"
REPO = "Aravindh-dev12/Aravindh-dev12"


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def normalize_command(raw: str) -> str:
    cmd = (raw or "").strip().lower().splitlines()[0].strip()
    if cmd.startswith("storm:"):
        cmd = cmd.split(":", 1)[1].strip()
    aliases = {
        "u": "up", "d": "down", "l": "left", "r": "right",
        "b": "boost", "restart": "reset",
    }
    return aliases.get(cmd, cmd)


def move_hazards(hazards, turn):
    out = []
    for i, (x, y) in enumerate(hazards):
        dx = 1 if (turn + i) % 2 == 0 else -1
        nx = (x + dx) % COLS
        ny = (y + (1 if i == 1 and turn % 3 == 0 else 0)) % ROWS
        out.append([nx, ny])
    return out


def next_target(turn):
    spots = [[7, 2], [6, 0], [8, 4], [4, 1], [7, 3], [2, 0]]
    return spots[(turn // 3) % len(spots)]


def apply(state, command):
    valid = {"up", "down", "left", "right", "boost", "reset", "tick"}
    if command not in valid:
        state["last"] = "IGNORED"
        return state, f"Unknown move `{command}`. Use one of the controls in the profile README."

    if command == "reset":
        state.update({
            "x": 1, "y": 2, "energy": 5, "score": 0, "turn": 0,
            "target": [7, 2], "hazards": [[3, 1], [5, 3], [6, 1]],
            "last": "RESET",
        })
        return state, "Game reset. VECTOR//STORM is ready."

    dx = dy = 0
    if command == "up":
        dy = -1
    elif command == "down":
        dy = 1
    elif command == "left":
        dx = -1
    elif command == "right":
        dx = 1
    elif command == "boost":
        # Dash two cells toward the target on the dominant axis.
        tx, ty = state["target"]
        if abs(tx - state["x"]) >= abs(ty - state["y"]):
            dx = 2 if tx > state["x"] else -2
        else:
            dy = 2 if ty > state["y"] else -2
        state["energy"] = max(1, state["energy"] - 1)

    state["x"] = clamp(state["x"] + dx, 0, COLS - 1)
    state["y"] = clamp(state["y"] + dy, 0, ROWS - 1)
    state["turn"] += 1
    state["hazards"] = move_hazards(state["hazards"], state["turn"])

    result = "MOVE"
    if [state["x"], state["y"]] == state["target"]:
        state["score"] += 100 + min(200, state["turn"] * 5)
        state["energy"] = min(5, state["energy"] + 1)
        state["target"] = next_target(state["turn"] + 1)
        result = "CORE CAPTURED"
    elif [state["x"], state["y"]] in state["hazards"]:
        state["energy"] -= 1
        state["score"] = max(0, state["score"] - 25)
        result = "HAZARD HIT"

    if state["energy"] <= 0:
        state["x"], state["y"], state["energy"] = 1, 2, 5
        state["score"] = max(0, state["score"] - 100)
        result = "CORE RESPAWNED"

    state["last"] = result
    return state, (
        f"`{command}` → **{result}** · score `{state['score']}` · "
        f"energy `{state['energy']}/5` · turn `{state['turn']}`"
    )


def move_url(command: str) -> str:
    title = quote(f"storm: {command}")
    body = quote(
        "VECTOR//STORM move generated from the profile README.\n\n"
        "Submit this issue to play the move. The bot will update the board and close the issue."
    )
    return f"https://github.com/{REPO}/issues/new?title={title}&body={body}"


def render_board(state) -> str:
    cols = list("ABCDEFGHI")
    hazards = {tuple(p) for p in state["hazards"]}
    target = tuple(state["target"])
    player = (state["x"], state["y"])

    lines = []
    lines.append("|   | " + " | ".join(cols) + " |")
    lines.append("|---|" + "---|" * COLS)
    for y in range(ROWS):
        cells = []
        for x in range(COLS):
            pos = (x, y)
            if pos == player and pos == target:
                cell = "🏆"
            elif pos == player:
                cell = "🔷"
            elif pos == target:
                cell = "🟢"
            elif pos in hazards:
                cell = "🔻"
            else:
                cell = "▪️"
            cells.append(cell)
        lines.append(f"| **{y + 1}** | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_section(state) -> str:
    energy = "🟩" * state["energy"] + "⬛" * (5 - state["energy"])
    board = render_board(state)
    return f'''{START}
### `02 / vector.storm.play`

<div align="center">

## `VECTOR//STORM`

**🔷 YOU** · **🟢 TARGET** · **🔻 HAZARD**

`SCORE {state['score']:04d}   ·   ENERGY {state['energy']}/5   ·   TURN {state['turn']:03d}   ·   LAST {state.get('last', 'READY')}`

`{energy}`

</div>

{board}

<div align="center">

|  |  |  |
|---|---|---|
|  | [⬆️ **UP**]({move_url('up')}) |  |
| [⬅️ **LEFT**]({move_url('left')}) | [⚡ **BOOST**]({move_url('boost')}) | [➡️ **RIGHT**]({move_url('right')}) |
|  | [⬇️ **DOWN**]({move_url('down')}) |  |

[♻️ **RESET RUN**]({move_url('reset')})

<sub>Click a move, submit the pre-filled issue, and GitHub Actions updates this board in README.md. No game SVG is used.</sub>

`capture 🟢 · dodge 🔻 · preserve energy · chase the moving field`

</div>
{END}'''


def update_readme(state):
    text = README.read_text(encoding="utf-8")
    section = render_section(state)
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if pattern.search(text):
        text = pattern.sub(section, text)
    else:
        old = re.compile(
            r"### `02 / vector\.storm(?:\.live)?`.*?(?=\n---\n\n### `03 / endpoints`)",
            re.S,
        )
        if not old.search(text):
            raise RuntimeError("Could not locate Vector Storm section in README.md")
        text = old.sub(section + "\n", text)
    README.write_text(text, encoding="utf-8")


def main():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    command = normalize_command(os.environ.get("GAME_COMMAND", "tick"))
    state, message = apply(state, command)
    STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    update_readme(state)
    MSG.write_text(message + "\n", encoding="utf-8")
    print(message)


if __name__ == "__main__":
    main()
