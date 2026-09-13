#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
from pathlib import Path

STATE = Path("game/vector_storm_state.json")
OUT = Path("assets/vector-storm-live.svg")
MSG = Path(".game_message")
COLS, ROWS = 9, 5


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def normalize_command(raw: str) -> str:
    cmd = (raw or "").strip().lower().splitlines()[0].strip()
    aliases = {"u": "up", "d": "down", "l": "left", "r": "right", "b": "boost", "restart": "reset"}
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
        return state, f"Unknown command `{command}`. Use `up`, `down`, `left`, `right`, `boost`, or `reset`."

    if command == "reset":
        state.update({"x": 1, "y": 2, "energy": 5, "score": 0, "turn": 0, "target": [7, 2], "hazards": [[3, 1], [5, 3], [6, 1]], "last": "RESET"})
        return state, "Game reset. VECTOR//STORM is ready."

    dx = dy = 0
    if command == "up": dy = -1
    elif command == "down": dy = 1
    elif command == "left": dx = -1
    elif command == "right": dx = 1
    elif command == "boost":
        dx = 2
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
    return state, f"`{command}` → **{result}** · score `{state['score']}` · energy `{state['energy']}/5` · turn `{state['turn']}`"


def render(state):
    W, H = 1200, 430
    ox, oy, cw, ch = 250, 120, 95, 52
    px = ox + state["x"] * cw + cw / 2
    py = oy + state["y"] * ch + ch / 2
    tx = ox + state["target"][0] * cw + cw / 2
    ty = oy + state["target"][1] * ch + ch / 2

    grid = []
    for r in range(ROWS + 1):
        y = oy + r * ch
        grid.append(f'<line x1="{ox}" y1="{y}" x2="{ox + COLS*cw}" y2="{y}" class="grid"/>')
    for c in range(COLS + 1):
        x = ox + c * cw
        grid.append(f'<line x1="{x}" y1="{oy}" x2="{x}" y2="{oy + ROWS*ch}" class="grid"/>')

    arrows = []
    for r in range(ROWS):
        for c in range(COLS):
            x = ox + c*cw + cw/2
            y = oy + r*ch + ch/2
            flip = -1 if (c+r+state['turn']) % 2 else 1
            arrows.append(f'<path d="M{x-11},{y} l{18*flip},0 l{-5*flip},-4 m{5*flip},4 l{-5*flip},4" class="flow"/>')

    hazards = []
    for i, (hx, hy) in enumerate(state["hazards"]):
        x = ox + hx*cw + cw/2
        y = oy + hy*ch + ch/2
        hazards.append(f'''<g transform="translate({x} {y})">
<polygon points="0,-15 15,0 0,15 -15,0" class="haz"/>
<circle r="22" fill="none" stroke="var(--red)" stroke-dasharray="3 6" opacity=".65"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="{4+i}s" repeatCount="indefinite"/></circle>
</g>''')

    energy_w = 130 * state["energy"] / 5
    last = html.escape(state.get("last", "READY"))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Live VECTOR STORM README game board">
<style>
:root{{--bg:#0d1117;--panel:#111820;--fg:#e6edf3;--muted:#8b949e;--line:#30363d;--blue:#58a6ff;--purple:#bc8cff;--green:#3fb950;--red:#f85149}}
.bg{{fill:var(--bg)}}.panel{{fill:var(--panel);stroke:var(--line)}}.fg{{fill:var(--fg)}}.muted{{fill:var(--muted)}}
.t{{font:700 15px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.08em}}.s{{font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.grid{{stroke:var(--line);stroke-width:1;opacity:.7}}.flow{{stroke:var(--blue);stroke-width:1.15;fill:none;opacity:.28}}.haz{{fill:#2b1618;stroke:var(--red);stroke-width:1.8}}
@media(prefers-color-scheme:light){{:root{{--bg:#fff;--panel:#f6f8fa;--fg:#24292f;--muted:#57606a;--line:#d0d7de;--blue:#0969da;--purple:#8250df;--green:#1a7f37;--red:#cf222e}}}}
</style>
<rect class="bg" width="1200" height="430" rx="18"/>
<text x="44" y="42" class="fg t">VECTOR//STORM · LIVE README GAME</text>
<text x="44" y="66" class="muted s">state changes when a player submits a move through the controller issue</text>
<line x1="44" y1="84" x2="1156" y2="84" stroke="var(--line)"/>

<rect x="44" y="112" width="170" height="198" rx="14" class="panel"/>
<text x="60" y="139" class="muted t">GAME STATE</text>
<text x="60" y="170" class="fg s">SCORE  {state['score']:04d}</text>
<text x="60" y="194" class="fg s">ENERGY {state['energy']}/5</text>
<text x="60" y="218" class="fg s">TURN   {state['turn']:03d}</text>
<text x="60" y="242" class="fg s">LAST   {last}</text>
<rect x="60" y="264" width="130" height="9" rx="5" fill="var(--line)"/>
<rect x="60" y="264" width="{energy_w:.1f}" height="9" rx="5" fill="var(--green)"><animate attributeName="opacity" values=".65;1;.65" dur="1.6s" repeatCount="indefinite"/></rect>
<text x="60" y="296" class="muted s">goal: capture ◉</text>

<rect x="236" y="106" width="880" height="286" rx="16" class="panel"/>
{''.join(grid)}
{''.join(arrows)}

<g transform="translate({tx} {ty})">
<circle r="11" fill="var(--green)"/>
<circle r="18" fill="none" stroke="var(--green)" opacity=".85"><animate attributeName="r" values="15;28;15" dur="1.8s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;.08;.9" dur="1.8s" repeatCount="indefinite"/></circle>
<text x="0" y="-25" text-anchor="middle" class="fg s">TARGET</text>
</g>

{''.join(hazards)}

<g transform="translate({px} {py})">
<polygon points="18,0 -12,-11 -7,0 -12,11" fill="var(--blue)" stroke="var(--fg)" stroke-width="1.2"/>
<circle r="24" fill="none" stroke="var(--blue)" opacity=".25"><animate attributeName="r" values="18;29;18" dur="1.2s" repeatCount="indefinite"/></circle>
</g>

<circle r="4" fill="var(--purple)" opacity=".75"><animateMotion dur="4.8s" repeatCount="indefinite" path="M280 350 C430 90 720 390 1080 145"/></circle>
<circle r="3" fill="var(--green)" opacity=".55"><animateMotion dur="4.8s" begin="-2.4s" repeatCount="indefinite" path="M280 350 C430 90 720 390 1080 145"/></circle>

<text x="250" y="416" class="muted s">REAL STATE · GitHub Actions updates this board after each move</text>
</svg>\n'''


def main():
    state = json.loads(STATE.read_text())
    command = normalize_command(os.environ.get("GAME_COMMAND", "tick"))
    state, message = apply(state, command)
    STATE.write_text(json.dumps(state, indent=2) + "\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(state))
    MSG.write_text(message + "\n")
    print(message)


if __name__ == "__main__":
    main()
