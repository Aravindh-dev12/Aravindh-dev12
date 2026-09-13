#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

from generate_math_profile import demo_data, graphql, normalize_user, path

OUT_DIR = Path("assets")


def identity_svg(stats: dict) -> str:
    """Render a live-data-seeded identity fingerprint without repeated counters."""
    phase = (stats["entropy"] + (stats["repos"] % 11) / 11.0) * math.pi
    petals = 5 + stats["longest_streak"] % 4
    twist = 2 + stats["active_days"] % 5

    outer = []
    inner = []
    for i in range(720):
        t = i / 719 * 2 * math.pi
        r1 = 116 + 27 * math.sin(petals * t + phase) + 9 * math.cos(3 * t + phase / 2)
        r2 = 76 + 18 * math.cos(twist * t - phase) + 7 * math.sin(5 * t)
        outer.append((415 + r1 * math.cos(t), 220 + 0.66 * r1 * math.sin(t)))
        inner.append((415 + r2 * math.cos(t), 220 + 0.66 * r2 * math.sin(t)))

    satellites = []
    for i in range(14):
        t = i / 14 * 2 * math.pi + phase / 3
        radius = 145 + 13 * math.sin((i + petals) * 0.83)
        x = 415 + radius * math.cos(t)
        y = 220 + 0.66 * radius * math.sin(t)
        fill = (
            "var(--hot)"
            if i % 5 == 0
            else ("var(--accent2)" if i % 2 else "var(--accent)")
        )
        duration = 3.2 + (i % 4) * 0.55
        begin = -i * 0.23
        satellites.append(
            f'''<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{fill}" opacity=".72">
  <animate attributeName="r" values="2.2;4.8;2.2" dur="{duration:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values=".25;.95;.25" dur="{duration:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>
</circle>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 360" role="img" aria-label="ARAVINDHAN / IDENTITY.STATE">
<style>
  :root{{--fg:#c9d1d9;--muted:#8b949e;--faint:#30363d;--accent:#58a6ff;--accent2:#bc8cff;--hot:#3fb950;--panel:#0d1117}}
  .bg{{fill:var(--panel)}}.fg{{fill:var(--fg)}}.muted{{fill:var(--muted)}}
  .label{{font:600 14px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.08em}}
  .small{{font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
  .eq{{font:15px "Times New Roman",serif;fill:var(--fg)}}
  .divider{{stroke:var(--faint);stroke-width:1}}
  @media(prefers-color-scheme:light){{:root{{--fg:#24292f;--muted:#57606a;--faint:#d0d7de;--accent:#0969da;--accent2:#8250df;--hot:#1a7f37;--panel:#fff}}}}
</style>
<rect class="bg" width="1200" height="360" rx="18"/>
<text x="48" y="48" class="fg label">ARAVINDHAN / IDENTITY.STATE</text>
<text x="48" y="74" class="muted small">principles stay stable · live data changes the phase portrait</text>
<line x1="48" y1="94" x2="1152" y2="94" class="divider"/>

<text x="48" y="126" class="muted label">01 / PHASE FINGERPRINT</text>
<text x="48" y="151" class="eq">z(t)=r(t)eⁱᵗ,   r(t)=1+a·sin(kt+φ)+b·cos(mt)</text>
<text x="48" y="174" class="muted small">live GitHub data seeds the geometry; identity is expressed as motion, not repeated counters</text>

<g opacity=".82">
  <animateTransform attributeName="transform" type="rotate" from="0 415 220" to="360 415 220" dur="31s" repeatCount="indefinite"/>
  <path d="{path(outer)}" fill="none" stroke="var(--accent)" stroke-width="1.7"/>
  {''.join(satellites)}
</g>
<g opacity=".58">
  <animateTransform attributeName="transform" type="rotate" from="360 415 220" to="0 415 220" dur="19s" repeatCount="indefinite"/>
  <path d="{path(inner)}" fill="none" stroke="var(--accent2)" stroke-width="1.3"/>
</g>
<ellipse cx="415" cy="220" rx="180" ry="118" fill="none" stroke="var(--faint)" stroke-width="1" opacity=".8"/>
<circle cx="415" cy="220" r="5" fill="var(--hot)">
  <animate attributeName="r" values="3;7;3" dur="3.4s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values=".45;1;.45" dur="3.4s" repeatCount="indefinite"/>
</circle>

<line x1="790" y1="116" x2="790" y2="324" class="divider"/>
<text x="832" y="128" class="muted label">OPERATING PRINCIPLES</text>

<circle cx="842" cy="163" r="4" fill="var(--accent)"><animate attributeName="opacity" values=".3;1;.3" dur="2.7s" repeatCount="indefinite"/></circle>
<text x="862" y="168" class="fg label">REASONING</text><text x="1010" y="168" class="muted small">model the unknown</text>

<circle cx="842" cy="203" r="4" fill="var(--accent2)"><animate attributeName="opacity" values=".3;1;.3" dur="3.3s" begin="-.8s" repeatCount="indefinite"/></circle>
<text x="862" y="208" class="fg label">ENGINEERING</text><text x="1010" y="208" class="muted small">make it executable</text>

<circle cx="842" cy="243" r="4" fill="var(--hot)"><animate attributeName="opacity" values=".3;1;.3" dur="2.9s" begin="-1.1s" repeatCount="indefinite"/></circle>
<text x="862" y="248" class="fg label">CURIOSITY</text><text x="1010" y="248" class="muted small">expand the search</text>

<circle cx="842" cy="283" r="4" fill="var(--accent)"><animate attributeName="opacity" values=".3;1;.3" dur="3.7s" begin="-1.9s" repeatCount="indefinite"/></circle>
<text x="862" y="288" class="fg label">SYSTEMS</text><text x="1010" y="288" class="muted small">connect the parts</text>
</svg>\n'''


def main() -> int:
    try:
        raw = graphql()
        source = "github"
    except Exception:
        raw = demo_data()
        source = "demo"

    stats = normalize_user(raw)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "identity-state.svg").write_text(identity_svg(stats), encoding="utf-8")
    print(f"[math-sections] refreshed identity-state.svg from {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
