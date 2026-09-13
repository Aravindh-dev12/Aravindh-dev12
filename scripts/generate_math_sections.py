#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

from generate_math_profile import demo_data, graphql, normalize_user, path

OUT_DIR = Path("assets")


def identity_svg(stats: dict) -> str:
    """Render a high-contrast, readable identity fingerprint."""
    phase = (stats["entropy"] + (stats["repos"] % 11) / 11.0) * math.pi
    petals = 5 + stats["longest_streak"] % 4
    twist = 2 + stats["active_days"] % 5

    # Three-column composition:
    # copy | animated fingerprint | operating principles.
    cx, cy = 635, 236

    outer = []
    inner = []
    for i in range(720):
        t = i / 719 * 2 * math.pi
        r1 = 94 + 21 * math.sin(petals * t + phase) + 7 * math.cos(3 * t + phase / 2)
        r2 = 61 + 14 * math.cos(twist * t - phase) + 5 * math.sin(5 * t)
        outer.append((cx + r1 * math.cos(t), cy + 0.64 * r1 * math.sin(t)))
        inner.append((cx + r2 * math.cos(t), cy + 0.64 * r2 * math.sin(t)))

    satellites = []
    for i in range(14):
        t = i / 14 * 2 * math.pi + phase / 3
        radius = 122 + 10 * math.sin((i + petals) * 0.83)
        x = cx + radius * math.cos(t)
        y = cy + 0.64 * radius * math.sin(t)
        fill = (
            "var(--hot)"
            if i % 5 == 0
            else ("var(--accent2)" if i % 2 else "var(--accent)")
        )
        duration = 3.2 + (i % 4) * 0.55
        begin = -i * 0.23
        satellites.append(
            f'''<circle cx="{x:.1f}" cy="{y:.1f}" r="3.8" fill="{fill}" opacity=".90">
  <animate attributeName="r" values="2.6;5.4;2.6" dur="{duration:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values=".45;1;.45" dur="{duration:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>
</circle>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 410" role="img" aria-label="ARAVINDHAN / IDENTITY.STATE">
<style>
  :root{{--fg:#e6edf3;--muted:#a8b3bf;--faint:#3a434d;--accent:#58a6ff;--accent2:#bc8cff;--hot:#3fb950;--panel:#0d1117;--panel2:#111820}}
  .bg{{fill:var(--panel)}}
  .fg{{fill:var(--fg)}}
  .muted{{fill:var(--muted)}}
  .title{{font:700 17px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.07em}}
  .label{{font:700 15px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.08em}}
  .small{{font:14px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
  .body{{font:13.5px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
  .eq{{font:19px "Times New Roman",serif;fill:var(--fg)}}
  .divider{{stroke:var(--faint);stroke-width:1.2}}
  .copy-panel{{fill:var(--panel2);stroke:var(--faint);stroke-width:1.2}}
  @media(prefers-color-scheme:light){{:root{{--fg:#24292f;--muted:#57606a;--faint:#c9d1d9;--accent:#0969da;--accent2:#8250df;--hot:#1a7f37;--panel:#fff;--panel2:#f6f8fa}}}}
</style>

<rect class="bg" width="1200" height="410" rx="18"/>
<text x="48" y="50" class="fg title">ARAVINDHAN / IDENTITY.STATE</text>
<text x="48" y="80" class="muted small">principles stay stable · live data changes the phase portrait</text>
<line x1="48" y1="104" x2="1152" y2="104" class="divider"/>

<text x="48" y="137" class="muted label">01 / PHASE FINGERPRINT</text>

<!-- Readability-first copy block -->
<rect x="42" y="154" width="455" height="126" rx="12" class="copy-panel" opacity=".98"/>
<text x="62" y="187" class="eq">z(t)=r(t)eⁱᵗ</text>
<text x="62" y="217" class="eq">r(t)=1+a·sin(kt+φ)+b·cos(mt)</text>
<text x="62" y="249" class="fg body">live GitHub data seeds the geometry.</text>
<text x="62" y="272" class="muted body">identity is motion — not repeated counters.</text>

<!-- Animated fingerprint -->
<g opacity=".95">
  <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="31s" repeatCount="indefinite"/>
  <path d="{path(outer)}" fill="none" stroke="var(--accent)" stroke-width="2.2"/>
  {''.join(satellites)}
</g>
<g opacity=".78">
  <animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="19s" repeatCount="indefinite"/>
  <path d="{path(inner)}" fill="none" stroke="var(--accent2)" stroke-width="1.8"/>
</g>
<ellipse cx="{cx}" cy="{cy}" rx="145" ry="96" fill="none" stroke="var(--faint)" stroke-width="1.2" opacity=".92"/>
<circle cx="{cx}" cy="{cy}" r="5.8" fill="var(--hot)">
  <animate attributeName="r" values="3.8;7.8;3.8" dur="3.4s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values=".55;1;.55" dur="3.4s" repeatCount="indefinite"/>
</circle>

<!-- Operating principles -->
<line x1="835" y1="130" x2="835" y2="340" class="divider"/>
<text x="867" y="143" class="muted label">OPERATING PRINCIPLES</text>

<circle cx="878" cy="184" r="4.8" fill="var(--accent)"><animate attributeName="opacity" values=".45;1;.45" dur="2.7s" repeatCount="indefinite"/></circle>
<text x="900" y="190" class="fg label">REASONING</text>
<text x="900" y="212" class="muted body">model the unknown</text>

<circle cx="878" cy="242" r="4.8" fill="var(--accent2)"><animate attributeName="opacity" values=".45;1;.45" dur="3.3s" begin="-.8s" repeatCount="indefinite"/></circle>
<text x="900" y="248" class="fg label">ENGINEERING</text>
<text x="900" y="270" class="muted body">make it executable</text>

<circle cx="878" cy="300" r="4.8" fill="var(--hot)"><animate attributeName="opacity" values=".45;1;.45" dur="2.9s" begin="-1.1s" repeatCount="indefinite"/></circle>
<text x="900" y="306" class="fg label">CURIOSITY</text>
<text x="900" y="328" class="muted body">expand the search</text>

<circle cx="1080" cy="184" r="4.8" fill="var(--accent)"><animate attributeName="opacity" values=".45;1;.45" dur="3.7s" begin="-1.9s" repeatCount="indefinite"/></circle>
<text x="1102" y="190" class="fg label">SYSTEMS</text>
<text x="1102" y="212" class="muted body">connect the parts</text>
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
