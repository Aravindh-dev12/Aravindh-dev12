#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import random
import sys
import urllib.request
from collections import Counter
from datetime import date, timedelta
from html import escape
from pathlib import Path

USER = os.getenv('GITHUB_USER', 'Aravindh-dev12')
TOKEN = os.getenv('GITHUB_TOKEN', '')
OUT = Path(os.getenv('MATH_PROFILE_OUT', 'assets/math-profile.svg'))

QUERY = '''
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        primaryLanguage { name color }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            weekday
          }
        }
      }
    }
  }
}
'''


def graphql() -> dict:
    if not TOKEN:
        raise RuntimeError('GITHUB_TOKEN is not set')
    payload = json.dumps({'query': QUERY, 'variables': {'login': USER}}).encode()
    req = urllib.request.Request(
        'https://api.github.com/graphql',
        data=payload,
        headers={
            'Authorization': f'bearer {TOKEN}',
            'Content-Type': 'application/json',
            'User-Agent': 'math-profile-generator',
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.load(response)
    if data.get('errors'):
        raise RuntimeError(data['errors'])
    return data['data']['user']


def demo_data() -> dict:
    rng = random.Random(12051999)
    today = date.today()
    start = today - timedelta(days=370)
    weeks = []
    total = 0
    cursor = start - timedelta(days=(start.weekday() + 1) % 7)
    for w in range(53):
        days = []
        for d in range(7):
            dt = cursor + timedelta(days=w * 7 + d)
            seasonal = 2.2 + 1.7 * math.sin(w / 5.3) + 1.2 * math.cos((w + d) / 3.2)
            burst = 7 if w in (9, 10, 26, 27, 40, 41) and d in (1, 2, 3, 4) else 0
            count = max(0, int(rng.gauss(max(0.5, seasonal + burst), 2.5)))
            if dt > today:
                count = 0
            total += count
            days.append({'contributionCount': count, 'date': dt.isoformat(), 'weekday': d})
        weeks.append({'contributionDays': days})
    return {
        'followers': {'totalCount': 0},
        'repositories': {
            'totalCount': 18,
            'nodes': [
                {'stargazerCount': 3, 'forkCount': 0, 'primaryLanguage': {'name': 'Python', 'color': '#3572A5'}},
                {'stargazerCount': 2, 'forkCount': 0, 'primaryLanguage': {'name': 'TypeScript', 'color': '#3178c6'}},
                {'stargazerCount': 0, 'forkCount': 0, 'primaryLanguage': {'name': 'Vue', 'color': '#41b883'}},
                {'stargazerCount': 0, 'forkCount': 0, 'primaryLanguage': {'name': 'JavaScript', 'color': '#f1e05a'}},
            ],
        },
        'contributionsCollection': {'contributionCalendar': {'totalContributions': total, 'weeks': weeks}},
    }


def normalize_user(raw: dict) -> dict:
    cal = raw['contributionsCollection']['contributionCalendar']
    weeks = cal['weeks'][-53:]
    matrix = [[0] * 7 for _ in range(53)]
    dates = [[''] * 7 for _ in range(53)]
    offset = 53 - len(weeks)
    for wi, week in enumerate(weeks, start=offset):
        for day in week['contributionDays']:
            wd = int(day['weekday'])
            if 0 <= wd < 7:
                matrix[wi][wd] = int(day['contributionCount'])
                dates[wi][wd] = day['date']

    repos = raw['repositories']
    langs = Counter()
    stars = 0
    forks = 0
    for node in repos.get('nodes') or []:
        stars += int(node.get('stargazerCount') or 0)
        forks += int(node.get('forkCount') or 0)
        lang = node.get('primaryLanguage')
        if lang and lang.get('name'):
            langs[lang['name']] += 1

    total_lang = sum(langs.values())
    entropy = 0.0
    if total_lang:
        for n in langs.values():
            p = n / total_lang
            entropy -= p * math.log2(p)

    flat = [matrix[w][d] for w in range(53) for d in range(7)]
    active_days = sum(v > 0 for v in flat)

    streak = longest = 0
    for v in flat:
        if v > 0:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 0

    current = 0
    for v in reversed(flat):
        if v > 0:
            current += 1
        elif current:
            break

    return {
        'matrix': matrix,
        'dates': dates,
        'total': int(cal['totalContributions']),
        'active_days': active_days,
        'longest_streak': longest,
        'current_streak': current,
        'repos': int(repos['totalCount']),
        'followers': int(raw['followers']['totalCount']),
        'stars': stars,
        'forks': forks,
        'languages': langs,
        'entropy': entropy,
    }


def lorenz_points(stats: dict, steps: int = 1900) -> list[tuple[float, float, float]]:
    sigma = 10.0 + (stats['repos'] % 7) * 0.08
    rho = 28.0 + (stats['total'] % 29) * 0.025
    beta = 8.0 / 3.0 + (stats['entropy'] % 1.0) * 0.03
    dt = 0.006
    x = 0.1 + (stats['followers'] % 11) / 50
    y = (stats['stars'] % 13) / 60
    z = (stats['active_days'] % 17) / 70
    pts = []
    for _ in range(steps):
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        x += dx * dt
        y += dy * dt
        z += dz * dt
        pts.append((x, y, z))
    return pts


def project_field(w: int, d: int, count: int) -> tuple[float, float]:
    h = math.log1p(count)
    x = 78 + w * 15.5 + d * 4.8
    y = 378 + d * 18.0 - h * 16.0 - w * 0.40
    return x, y


def path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ''
    return 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in points)


def render_svg(stats: dict) -> str:
    m = stats['matrix']
    max_count = max(max(row) for row in m) or 1

    mesh = []
    for d in range(7):
        pts = [project_field(w, d, m[w][d]) for w in range(53)]
        mesh.append(f'<path class="mesh mesh-day" d="{path(pts)}" style="animation-delay:{d * -0.35:.2f}s"/>')
    for w in range(53):
        pts = [project_field(w, d, m[w][d]) for d in range(7)]
        opacity = 0.13 + (w % 4) * 0.025
        mesh.append(f'<path class="mesh" opacity="{opacity:.2f}" d="{path(pts)}"/>')

    dots = []
    for w in range(53):
        for d in range(7):
            count = m[w][d]
            if count <= 0:
                continue
            x, y = project_field(w, d, count)
            r = 1.8 + 3.3 * math.sqrt(count / max_count)
            delay = -((w * 7 + d) % 37) / 5
            dots.append(
                f'<circle class="sample" cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" '
                f'opacity="{0.38 + 0.55 * count / max_count:.2f}" style="animation-delay:{delay:.2f}s"/>'
            )

    lp = lorenz_points(stats)
    xs = [p[0] for p in lp]
    zs = [p[2] for p in lp]
    xmin, xmax = min(xs), max(xs)
    zmin, zmax = min(zs), max(zs)
    lpts = []
    for x, _, z in lp[120:]:
        px = 955 + (x - xmin) / (xmax - xmin) * 185
        py = 210 + (z - zmin) / (zmax - zmin) * 165
        lpts.append((px, py))
    lpath = path(lpts)

    languages = stats['languages'].most_common(4)
    language_text = ' · '.join(name for name, _ in languages) or '∅'
    sigma = 10.0 + (stats['repos'] % 7) * 0.08
    rho = 28.0 + (stats['total'] % 29) * 0.025
    beta = 8.0 / 3.0 + (stats['entropy'] % 1.0) * 0.03

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 700" role="img" aria-labelledby="title desc">
<title id="title">{escape(USER)} — mathematical GitHub state</title>
<desc id="desc">A live mathematical portrait generated from GitHub contributions. Daily contribution counts form a logarithmic height field, while profile statistics seed a Lorenz attractor.</desc>
<style>
  :root {{ --fg:#c9d1d9; --muted:#8b949e; --faint:#30363d; --accent:#58a6ff; --accent2:#bc8cff; --hot:#3fb950; --panel:#0d1117; }}
  .bg {{ fill:var(--panel); }} .fg {{ fill:var(--fg); }} .muted {{ fill:var(--muted); }}
  .label {{ font:600 14px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; letter-spacing:.08em; }}
  .small {{ font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}
  .metric {{ font:700 25px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; fill:var(--fg); }}
  .eq {{ font:15px "Times New Roman",serif; fill:var(--fg); }}
  .mesh {{ fill:none; stroke:var(--accent); stroke-width:1; vector-effect:non-scaling-stroke; }}
  .mesh-day {{ stroke-width:1.4; opacity:.52; stroke-dasharray:7 7; animation:flow 8s linear infinite; }}
  .sample {{ fill:var(--hot); animation:pulse 3.4s ease-in-out infinite; }}
  .lorenz {{ fill:none; stroke:var(--accent2); stroke-width:1.25; opacity:.82; stroke-dasharray:5 5; animation:flow 18s linear infinite; }}
  .axis,.divider {{ stroke:var(--faint); stroke-width:1; }}
  .formula-box {{ fill:none; stroke:var(--faint); rx:12; }}
  @keyframes flow {{ to {{ stroke-dashoffset:-84; }} }}
  @keyframes pulse {{ 0%,100%{{opacity:.35}} 50%{{opacity:1}} }}
  @media (prefers-color-scheme: light) {{
    :root {{ --fg:#24292f; --muted:#57606a; --faint:#d0d7de; --accent:#0969da; --accent2:#8250df; --hot:#1a7f37; --panel:#ffffff; }}
  }}
</style>
<rect class="bg" width="1200" height="700" rx="18"/>
<text x="48" y="48" class="fg label">ARAVINDHAN / MATHEMATICAL STATE</text>
<text x="48" y="76" class="muted small">profile(t) = data × structure × iteration</text>
<line x1="48" y1="96" x2="1152" y2="96" class="divider"/>

<text x="48" y="128" class="muted label">01 / CONTRIBUTION FIELD</text>
<text x="48" y="154" class="eq">c(w,d) ∈ ℕ,   h(w,d) = ln(1 + c(w,d))</text>
<text x="48" y="177" class="muted small">53 weeks × 7 days → discrete scalar field → isometric surface</text>
<text x="48" y="202" class="muted small">Σc = {stats['total']:,}  ·  active = {stats['active_days']}  ·  streak_max = {stats['longest_streak']}  ·  repos = {stats['repos']}</text>

<line x1="78" y1="498" x2="895" y2="474" class="axis"/>
<line x1="78" y1="498" x2="110" y2="610" class="axis"/>
<g aria-label="Contribution surface">{''.join(mesh)}{''.join(dots)}</g>
<text x="48" y="616" class="muted small">w → time</text>
<text x="104" y="642" class="muted small">d → weekday</text>
<text x="48" y="674" class="muted small">height = log(1 + daily contributions)</text>

<line x1="918" y1="118" x2="918" y2="640" class="divider"/>
<text x="950" y="128" class="muted label">02 / CHAOTIC SIGNATURE</text>
<text x="950" y="153" class="eq">ẋ=σ(y−x)</text>
<text x="950" y="174" class="eq">ẏ=x(ρ−z)−y</text>
<text x="950" y="195" class="eq">ż=xy−βz</text>
<path class="lorenz" d="{lpath}"/>
<text x="950" y="392" class="muted small">σ = {sigma:.3f}</text>
<text x="950" y="412" class="muted small">ρ = {rho:.3f}</text>
<text x="950" y="432" class="muted small">β = {beta:.3f}</text>

<rect x="942" y="456" width="210" height="184" class="formula-box"/>
<text x="960" y="484" class="muted label">STATE VECTOR</text>
<text x="960" y="520" class="metric">{stats['total']:,}</text>
<text x="960" y="539" class="muted small">Σ contributions / year</text>
<text x="960" y="573" class="fg label">{stats['active_days']} active days</text>
<text x="960" y="595" class="fg label">{stats['longest_streak']}d max streak</text>
<text x="960" y="617" class="fg label">{stats['repos']} public repos</text>
<text x="960" y="636" class="muted small">H(lang)={stats['entropy']:.2f} bits</text>
<text x="950" y="668" class="muted small">{escape(language_text)}</text>
</svg>
'''


def main() -> int:
    try:
        raw = graphql()
        source = 'github'
    except Exception as exc:
        print(f'[math-profile] GitHub fetch unavailable: {exc}', file=sys.stderr)
        raw = demo_data()
        source = 'demo'

    stats = normalize_user(raw)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render_svg(stats), encoding='utf-8')
    print(f"[math-profile] wrote {OUT} from {source}: {stats['total']} contributions, {stats['repos']} repos, H={stats['entropy']:.2f}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
