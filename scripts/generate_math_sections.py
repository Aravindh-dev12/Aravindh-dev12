#!/usr/bin/env python3
from __future__ import annotations

import math
from html import escape
from pathlib import Path

from generate_math_profile import demo_data, graphql, normalize_user, path

OUT_DIR = Path('assets')


def common_style() -> str:
    return '''
<style>
  :root { --fg:#c9d1d9; --muted:#8b949e; --faint:#30363d; --accent:#58a6ff; --accent2:#bc8cff; --hot:#3fb950; --panel:#0d1117; }
  .bg { fill:var(--panel); } .fg { fill:var(--fg); } .muted { fill:var(--muted); }
  .label { font:600 14px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; letter-spacing:.08em; }
  .small { font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }
  .metric { font:700 23px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; fill:var(--fg); }
  .eq { font:15px "Times New Roman",serif; fill:var(--fg); }
  .divider,.axis { stroke:var(--faint); stroke-width:1; }
  .flow { fill:none; stroke:var(--accent); stroke-width:1.4; stroke-dasharray:7 7; animation:flow 8s linear infinite; vector-effect:non-scaling-stroke; }
  .flow2 { fill:none; stroke:var(--accent2); stroke-width:1.25; stroke-dasharray:5 6; animation:flow 13s linear infinite reverse; vector-effect:non-scaling-stroke; }
  .hot { fill:var(--hot); animation:pulse 3.2s ease-in-out infinite; }
  .node { fill:var(--accent); animation:pulse 3.8s ease-in-out infinite; }
  .panelbox { fill:none; stroke:var(--faint); rx:12; }
  @keyframes flow { to { stroke-dashoffset:-84; } }
  @keyframes pulse { 0%,100%{opacity:.35} 50%{opacity:1} }
  @media (prefers-color-scheme: light) {
    :root { --fg:#24292f; --muted:#57606a; --faint:#d0d7de; --accent:#0969da; --accent2:#8250df; --hot:#1a7f37; --panel:#ffffff; }
  }
</style>'''


def svg_shell(title: str, subtitle: str, body: str, height: int = 360) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {height}" role="img" aria-label="{escape(title)}">
{common_style()}
<rect class="bg" width="1200" height="{height}" rx="18"/>
<text x="48" y="48" class="fg label">{escape(title)}</text>
<text x="48" y="74" class="muted small">{escape(subtitle)}</text>
<line x1="48" y1="94" x2="1152" y2="94" class="divider"/>
{body}
</svg>\n'''


def identity_svg(stats: dict) -> str:
    a = 2 + stats['repos'] % 5
    b = 3 + stats['active_days'] % 7
    delta = (stats['entropy'] % 1.0) * math.pi
    pts = []
    for i in range(900):
        t = i / 899 * 2 * math.pi
        x = 415 + 310 * math.sin(a * t + delta)
        y = 220 + 105 * math.sin(b * t)
        pts.append((x, y))
    orbit = path(pts)

    phase_pts = []
    for i in range(360):
        t = i / 359 * 2 * math.pi
        r = 42 + 9 * math.sin((stats['longest_streak'] % 9 + 3) * t)
        phase_pts.append((1000 + r * math.cos(t), 214 + r * math.sin(t)))

    body = f'''
<text x="48" y="126" class="muted label">01 / STATE ORBIT</text>
<text x="48" y="151" class="eq">x(t)=sin({a}t+δ),   y(t)=sin({b}t)</text>
<text x="48" y="174" class="muted small">parameters seeded by repositories · activity · language entropy</text>
<path d="{orbit}" class="flow" opacity=".74"/>
<path d="{orbit}" class="flow2" opacity=".38" transform="translate(0 3)"/>
<circle class="hot" cx="415" cy="220" r="4.8"/>

<line x1="830" y1="116" x2="830" y2="324" class="divider"/>
<text x="862" y="128" class="muted label">STATE VECTOR</text>
<text x="862" y="166" class="metric">{stats['repos']}</text><text x="930" y="166" class="muted small">repos</text>
<text x="862" y="200" class="metric">{stats['active_days']}</text><text x="930" y="200" class="muted small">active days</text>
<text x="862" y="234" class="metric">{stats['longest_streak']}d</text><text x="930" y="234" class="muted small">max streak</text>
<text x="862" y="268" class="metric">{stats['entropy']:.2f}</text><text x="930" y="268" class="muted small">H(lang)</text>
<path d="{path(phase_pts)}" class="flow2" opacity=".74"/>
'''
    return svg_shell('ARAVINDHAN / IDENTITY.STATE', 'identity = state × motion × constraints', body)


def systems_svg(stats: dict) -> str:
    langs = stats['languages'].most_common(4)
    if not langs:
        langs = [('∅', 1)]
    while len(langs) < 4:
        langs.append((f'λ{len(langs)+1}', 0))
    total = max(1, sum(v for _, v in langs))
    waves = []
    colors = ['flow', 'flow2', 'flow', 'flow2']
    for idx, (name, count) in enumerate(langs[:4]):
        amp = 22 + 48 * count / total
        freq = 1.0 + idx * .45 + (stats['repos'] % 5) * .04
        phase = (stats['stars'] + idx * 7) * .19
        pts = []
        for i in range(160):
            x = 80 + i * 5.0
            u = i / 159 * 2 * math.pi
            y = 210 + amp * math.sin(freq * u + phase) + idx * 3
            pts.append((x, y))
        waves.append(f'<path d="{path(pts)}" class="{colors[idx]}" opacity="{0.38 + idx*0.12:.2f}" style="animation-delay:{-idx*1.7:.1f}s"/>')

    coupled = []
    for i in range(180):
        x = 80 + i * 4.45
        u = i / 179 * 2 * math.pi
        y = 210
        for idx, (_, count) in enumerate(langs[:4]):
            amp = 10 + 22 * count / total
            freq = 1.0 + idx * .45 + (stats['repos'] % 5) * .04
            phase = (stats['stars'] + idx * 7) * .19
            y += amp * math.sin(freq * u + phase) / 2.5
        coupled.append((x, y))

    labels = ''.join(
        f'<text x="930" y="{155 + i*34}" class="fg label">{escape(name)}</text><text x="1100" y="{155 + i*34}" class="muted small">{count} repos</text>'
        for i, (name, count) in enumerate(langs[:4])
    )
    body = f'''
<text x="48" y="126" class="muted label">03 / COUPLED OSCILLATORS</text>
<text x="48" y="151" class="eq">θ̇ᵢ = ωᵢ + K Σ sin(θⱼ−θᵢ)</text>
<text x="48" y="174" class="muted small">top languages become oscillators · repository distribution controls amplitude</text>
{''.join(waves)}
<path d="{path(coupled)}" class="flow" style="stroke-width:2.1" opacity=".9"/>
<circle class="hot" cx="80" cy="210" r="4.2"/><circle class="node" cx="875" cy="210" r="4.2"/>
<line x1="900" y1="116" x2="900" y2="324" class="divider"/>
<text x="930" y="128" class="muted label">LANGUAGE MODES</text>
{labels}
<text x="930" y="302" class="muted small">coupling K ≈ {0.35 + stats['entropy']*0.11:.3f}</text>
'''
    return svg_shell('ARAVINDHAN / SYSTEMS.IN.MOTION', 'repositories → modes → coupled signal', body)


def operating_svg(stats: dict) -> str:
    weekly = [sum(stats['matrix'][w]) for w in range(53)]
    maxw = max(weekly) or 1
    signal = []
    smooth = []
    for i, val in enumerate(weekly):
        x = 70 + i * 15.0
        y = 235 - 120 * val / maxw
        signal.append((x, y))
        lo, hi = max(0, i-2), min(53, i+3)
        avg = sum(weekly[lo:hi]) / (hi-lo)
        smooth.append((x, 235 - 120 * avg / maxw))

    spectrum = []
    n = len(weekly)
    mean = sum(weekly)/n
    centered = [v-mean for v in weekly]
    for k in range(1, 17):
        re = sum(centered[j] * math.cos(2*math.pi*k*j/n) for j in range(n))
        im = -sum(centered[j] * math.sin(2*math.pi*k*j/n) for j in range(n))
        spectrum.append(math.sqrt(re*re + im*im))
    maxs = max(spectrum) or 1
    bars = ''.join(
        f'<rect x="{920+i*13}" y="{280-110*v/maxs:.1f}" width="7" height="{110*v/maxs:.1f}" fill="var(--accent2)" opacity="{0.35 + 0.5*v/maxs:.2f}"/>'
        for i, v in enumerate(spectrum)
    )
    body = f'''
<text x="48" y="126" class="muted label">04 / ACTIVITY SIGNAL</text>
<text x="48" y="151" class="eq">s(w)=Σ₍d₎ c(w,d)</text>
<text x="48" y="174" class="muted small">weekly contribution signal · smoothed trend · discrete spectrum</text>
<line x1="70" y1="235" x2="860" y2="235" class="axis"/>
<path d="{path(signal)}" class="flow" opacity=".72"/>
<path d="{path(smooth)}" class="flow2" style="stroke-width:2" opacity=".9"/>
<circle class="hot" cx="850" cy="{signal[-1][1]:.1f}" r="4.5"/>
<line x1="890" y1="116" x2="890" y2="324" class="divider"/>
<text x="920" y="128" class="muted label">FREQUENCY CONTENT</text>
{bars}
<text x="920" y="306" class="muted small">dominant rhythms / last 53 weeks</text>
'''
    return svg_shell('ARAVINDHAN / OPERATING.SYSTEM', 'activity behaves like a sampled signal', body)


def constraints_svg(stats: dict) -> str:
    entropy = stats['entropy']
    active_ratio = stats['active_days'] / 371.0
    alpha = 0.55 + active_ratio * 1.6
    beta = 0.45 + (stats['longest_streak'] % 17) / 17
    gamma = 0.7 + (entropy % 2.5) / 2.5

    field = []
    for gy in range(7):
        for gx in range(17):
            x = 70 + gx * 43
            y = 135 + gy * 27
            nx = (gx - 8) / 8
            ny = (gy - 3) / 3
            vx = math.sin(alpha*ny*math.pi) + gamma*nx*.35
            vy = math.cos(beta*nx*math.pi) - gamma*ny*.28
            mag = math.hypot(vx, vy) or 1
            length = 9 + 9 * min(1, mag)
            ex = x + vx/mag*length
            ey = y + vy/mag*length
            field.append(f'<path d="M{x:.1f},{y:.1f} L{ex:.1f},{ey:.1f}" class="flow" opacity=".34" style="animation-delay:{-(gx+gy)*.12:.2f}s"/>')
            if (gx+gy) % 5 == 0:
                field.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="2.1" class="hot" style="animation-delay:{-(gx*gy%11)*.2:.2f}s"/>')

    contours = []
    for r in (34, 56, 78, 100):
        pts = []
        for i in range(240):
            t = i/239*2*math.pi
            rr = r * (1 + .12*math.sin((3 + stats['repos']%4)*t + entropy))
            x = 1015 + rr*math.cos(t)
            y = 215 + .62*rr*math.sin(t)
            pts.append((x, y))
        contours.append(f'<path d="{path(pts)}" class="flow2" opacity="{0.25 + r/220:.2f}"/>')

    body = f'''
<text x="48" y="126" class="muted label">05 / VECTOR FIELD</text>
<text x="48" y="151" class="eq">F(x,y)=⟨sin(απy)+γx, cos(βπx)−γy⟩</text>
<text x="48" y="174" class="muted small">field parameters seeded by activity density · streak length · language entropy</text>
{''.join(field)}
<line x1="860" y1="116" x2="860" y2="324" class="divider"/>
<text x="892" y="128" class="muted label">CONSTRAINT BASIN</text>
{''.join(contours)}
<text x="892" y="302" class="muted small">α={alpha:.3f} · β={beta:.3f} · γ={gamma:.3f}</text>
'''
    return svg_shell('ARAVINDHAN / DESIGN.CONSTRAINTS', 'constraints shape the field of possible systems', body)


def main() -> int:
    try:
        raw = graphql()
        source = 'github'
    except Exception:
        raw = demo_data()
        source = 'demo'
    stats = normalize_user(raw)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        'identity-state.svg': identity_svg(stats),
        'systems-in-motion.svg': systems_svg(stats),
        'operating-system.svg': operating_svg(stats),
        'design-constraints.svg': constraints_svg(stats),
    }
    for name, content in outputs.items():
        (OUT_DIR / name).write_text(content, encoding='utf-8')
    print(f"[math-sections] wrote {len(outputs)} live math panels from {source}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
