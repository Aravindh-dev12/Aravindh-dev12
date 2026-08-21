import datetime as dt
import html
import os
from pathlib import Path

import requests

USER_NAME = os.getenv("USER_NAME", "Aravindh-dev12")
TOKEN = os.getenv("ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
GRAPHQL_URL = "https://api.github.com/graphql"
README_FILE = Path("README.md")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Aravindh-dev12-profile-updater",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

BATMAN_ASCII = [
    "           ;@s                2B,          ",
    "           i&M.    .....     :S&;          ",
    "           sB#HAAAAAAA25522A5GB&s          ",
    "           A###SHM33533MMHHG#99&5          ",
    "          .5HGGSSGHHGGGSSSGGS9BBH,         ",
    "          ;3MS#9##SSSSS#99999BBB#r         ",
    "          XhG9B9##SGS###99B&&&BB95         ",
    "          5H9&&BB999999B9B&&&&&BBM,        ",
    "         .hSB&&&&BBB999BBBB&&&&&&G:        ",
    "         .hBB&&&BBBBBBBBBB&&&&&B&S;        ",
    "          5BB9BBBB&&&&&&&&&&&&BB&S:        ",
    "          ABBBBBB&&&&&&&&&&&&&&B9M,        ",
    "          :HS9@&&&&&&&&&&&&&&&&&Hr         ",
    "           XH9B&&&&&&&&&&&&&&&&@M          ",
    "           ;#@@&&&&&&B&&&&&@@@@9A          ",
    "           ihMB&&&&&&&&&&&&&&&#35:         ",
    "          2Bh2#B##9B&&&&&B99#BG39G,        ",
    "         ;hBShH&#S##9BB99###9BHG9Mr        ",
    "         XG#BBG9B9##99B99##9B99&#H5.       ",
    "        .3BBB&&BBBB9#S####9B&&@BB#Hi       ",
    "        ;G&&&B&&&&&B9###9B&&@@&B&B#2       ",
    "      .:5#&&@&&&&&@@@@&&@@@@@&B&&&9G5H2,   ",
    "  :irX5hMMH&@&&&@@@&&&&@&&&&@&&&@&&BB@5.sr,",
    ";2H###9SHS9&&&&&&@@@@&&&&@&&&&@&&@@@&&#HSHs",
    "M###999##BB&&&&&&&&&&&&&&@&&&@@&&@@@@&&&Bh5",
]

THEMES = {
    "dark": {
        "background": "#161b22",
        "text": "#c9d1d9",
        "key": "#f0c419",
        "value": "#a5d6ff",
        "muted": "#616e7f",
        "ascii": "#c9d1d9",
    },
    "light": {
        "background": "#f6f8fa",
        "text": "#24292f",
        "key": "#953800",
        "value": "#0a3069",
        "muted": "#8c959f",
        "ascii": "#24292f",
    },
}

RIGHT_X = 390
VALUE_X = 610
CHAR_WIDTH = 9.6


def github_activity():
    now = dt.datetime.now(dt.timezone.utc)
    start = now - dt.timedelta(days=364)

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        followers { totalCount }
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """

    variables = {
        "login": USER_NAME,
        "from": start.isoformat().replace("+00:00", "Z"),
        "to": now.isoformat().replace("+00:00", "Z"),
    }

    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])

    user = payload.get("data", {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {USER_NAME}")

    collection = user["contributionsCollection"]
    calendar = collection["contributionCalendar"]
    days = [
        day
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]

    active_days = sum(day["contributionCount"] > 0 for day in days)
    streak = current_streak(days, now.date())

    return {
        "contrib_data": calendar["totalContributions"],
        "streak_data": f"{streak} day" + ("" if streak == 1 else "s"),
        "commit_data": collection["totalCommitContributions"],
        "active_data": active_days,
        "follower_data": user["followers"]["totalCount"],
        "updated_data": now.strftime("%Y-%m-%d UTC"),
        "cache_stamp": now.strftime("%Y%m%d%H%M"),
    }


def current_streak(days, today):
    if not days:
        return 0

    counts = {dt.date.fromisoformat(day["date"]): day["contributionCount"] for day in days}
    cursor = today

    if counts.get(cursor, 0) == 0:
        cursor -= dt.timedelta(days=1)

    streak = 0
    while counts.get(cursor, 0) > 0:
        streak += 1
        cursor -= dt.timedelta(days=1)
    return streak


def fmt(value):
    return f"{value:,}" if isinstance(value, int) else str(value)


def leader_dots(label):
    prefix_chars = 2 + len(label) + 1
    used_width = prefix_chars * CHAR_WIDTH
    gap_width = max(0, VALUE_X - RIGHT_X - used_width)
    dot_count = max(3, int(gap_width / CHAR_WIDTH) - 2)
    return " " + "." * dot_count + " "


def fixed_line(y, label, value, element_id=None):
    safe_label = html.escape(label)
    safe_value = html.escape(fmt(value))
    dots_id = f' id="{element_id}_dots"' if element_id else ""
    value_id = f' id="{element_id}"' if element_id else ""
    return (
        f'<tspan x="{RIGHT_X}" y="{y}" class="cc">. </tspan>'
        f'<tspan class="key">{safe_label}</tspan>:'
        f'<tspan class="cc"{dots_id}>{html.escape(leader_dots(label))}</tspan>'
        f'<tspan x="{VALUE_X}" class="value"{value_id}>{safe_value}</tspan>'
    )


def stat_line(y, label, element_id, value):
    return fixed_line(y, label, value, element_id)


def bat_swarm(theme):
    bat = '<path id="mini-bat" d="M0 4 L4 1 L7 3 L10 0 L13 3 L16 1 L20 4 L16 5 L14 8 L10 6 L6 8 L4 5 Z"/>'
    flights = [
        ("0s", "4.2s", "M190,260 C95,170 105,65 280,24 C470,-18 720,18 935,105"),
        ("0.20s", "4.8s", "M185,270 C65,245 25,125 160,55 C350,-42 695,-5 955,150"),
        ("0.40s", "4.5s", "M200,250 C315,150 430,52 610,38 C790,24 920,105 972,220"),
        ("0.60s", "5.1s", "M180,265 C85,320 55,438 220,505 C430,590 730,530 945,390"),
        ("0.80s", "4.4s", "M205,250 C350,315 480,468 670,505 C835,537 950,430 975,305"),
        ("1.00s", "5.3s", "M175,255 C85,200 55,95 245,55 C470,8 735,72 930,190"),
        ("1.20s", "4.7s", "M195,275 C260,390 420,510 655,490 C840,474 950,355 970,220"),
        ("1.40s", "5.0s", "M190,245 C265,145 400,66 575,65 C760,65 905,150 970,285"),
        ("1.60s", "4.3s", "M205,268 C270,360 405,445 565,478 C755,515 900,450 958,350"),
        ("1.80s", "5.4s", "M185,250 C135,150 175,55 365,20 C575,-18 810,60 960,175"),
        ("2.00s", "4.6s", "M200,270 C120,350 130,462 325,515 C540,575 805,490 952,370"),
        ("2.20s", "5.2s", "M180,258 C85,275 35,365 140,458 C290,590 640,565 880,445"),
        ("2.40s", "4.9s", "M195,252 C315,205 450,105 635,92 C805,80 925,150 970,255"),
        ("2.60s", "4.1s", "M185,265 C120,215 125,105 310,65 C520,18 780,98 940,225"),
        ("2.80s", "5.5s", "M205,275 C330,395 500,500 710,480 C855,465 940,385 970,290"),
        ("3.00s", "4.6s", "M178,250 C80,160 110,48 300,22 C520,-10 780,45 955,145"),
        ("3.20s", "5.0s", "M192,270 C105,330 78,430 235,495 C445,582 760,510 950,370"),
        ("3.40s", "4.4s", "M205,248 C345,175 485,82 665,72 C835,62 940,150 975,275"),
    ]

    pieces = [f'<defs>{bat}</defs>', f'<g fill="{theme["ascii"]}" pointer-events="none">']
    for index, (begin, duration, path) in enumerate(flights):
        scale = 0.72 + (index % 5) * 0.10
        pieces.append(
            f'<g opacity="0.8">'
            f'<use href="#mini-bat" transform="scale({scale:.2f})"/>'
            f'<animate attributeName="opacity" values="0.18;0.95;0.65;0.18" keyTimes="0;0.22;0.76;1" '
            f'begin="{begin}" dur="{duration}" repeatCount="indefinite"/>'
            f'<animateMotion path="{path}" begin="{begin}" dur="{duration}" repeatCount="indefinite" rotate="auto"/>'
            f'</g>'
        )
    pieces.append('</g>')
    return "\n".join(pieces)


def render_svg(theme_name, stats):
    t = THEMES[theme_name]
    ascii_lines = "\n".join(
        f'<tspan x="15" y="{30 + i * 20}">{html.escape(line)}</tspan>'
        for i, line in enumerate(BATMAN_ASCII)
    )

    profile_lines = "\n".join([
        fixed_line(50, "Role", "AI Builder · Full-Stack Developer"),
        fixed_line(70, "Focus", "LLM · RAG · Agents · Web · Flutter"),
        fixed_line(90, "Stack", "Python · TypeScript · Dart · GitHub"),
        fixed_line(110, "Status", "Building · Learning · Shipping"),
    ])

    focus_lines = "\n".join([
        fixed_line(170, "AI", "LLM systems · RAG · agent workflows"),
        fixed_line(190, "Apps", "Web products · Flutter · automation"),
        fixed_line(210, "Research", "Neuro-symbolic · inference · retrieval"),
        fixed_line(230, "Mode", "Build in the shadows. Ship in the light."),
    ])

    dynamic = "\n".join([
        stat_line(286, "Contributions", "contrib_data", stats["contrib_data"]),
        stat_line(306, "Current Streak", "streak_data", stats["streak_data"]),
        stat_line(326, "Commits", "commit_data", stats["commit_data"]),
        stat_line(346, "Active Days", "active_data", stats["active_data"]),
        stat_line(366, "Followers", "follower_data", stats["follower_data"]),
        stat_line(386, "Last Refresh", "updated_data", stats["updated_data"]),
    ])

    footer_lines = "\n".join([
        fixed_line(426, "Signal", "The code is the signal."),
        fixed_line(446, "Handle", "@Aravindh-dev12"),
    ])

    swarm = bat_swarm(t)

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="530px" font-size="16px" role="img" aria-label="Aravindhan Batman ASCII GitHub profile card">
<style>
@font-face {{ src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback'; font-display: swap; -webkit-size-adjust: 109%; size-adjust: 109%; }}
.key {{fill: {t['key']};}} .value {{fill: {t['value']};}} .cc {{fill: {t['muted']};}} text, tspan {{white-space: pre;}}
</style>
<rect width="985px" height="530px" fill="{t['background']}" rx="15"/>
<text x="15" y="30" fill="{t['ascii']}" class="ascii" font-size="14px">
{ascii_lines}
</text>
<text x="{RIGHT_X}" y="30" fill="{t['text']}">
<tspan x="{RIGHT_X}" y="30">aravindhan@batcave</tspan> -—————————————————————————————————————————-—-
{profile_lines}
<tspan x="{RIGHT_X}" y="130" class="cc">. </tspan>
<tspan x="{RIGHT_X}" y="150">- Current Focus</tspan> -—————————————————————————————————————————-—-
{focus_lines}
<tspan x="{RIGHT_X}" y="250" class="cc">. </tspan>
<tspan x="{RIGHT_X}" y="266">- GitHub Activity · rolling 365 days</tspan> -——————————————————————-
{dynamic}
{footer_lines}
</text>
{swarm}
</svg>'''


def render_readme(cache_stamp):
    return f'''<!-- daily-refresh: {cache_stamp} -->
<div align="center">
  <a href="https://github.com/{USER_NAME}">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/{USER_NAME}/{USER_NAME}/main/dark_mode.svg?v={cache_stamp}">
      <img width="100%" alt="Aravindhan's Batman ASCII developer profile with daily GitHub activity" src="https://raw.githubusercontent.com/{USER_NAME}/{USER_NAME}/main/light_mode.svg?v={cache_stamp}">
    </picture>
  </a>

  <p><em>"It's not who I am underneath, but what I do that defines me."</em></p>
</div>
'''


def main():
    stats = github_activity()
    Path("dark_mode.svg").write_text(render_svg("dark", stats), encoding="utf-8")
    Path("light_mode.svg").write_text(render_svg("light", stats), encoding="utf-8")
    README_FILE.write_text(render_readme(stats["cache_stamp"]), encoding="utf-8")

    printable = {key: value for key, value in stats.items() if key != "cache_stamp"}
    print("Updated Batman profile:", printable)


if __name__ == "__main__":
    main()
