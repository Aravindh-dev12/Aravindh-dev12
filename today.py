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
        "cache_stamp": now.strftime("%Y%m%d%H%M%S"),
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


BAT_PATH = (
    "M0,-11 L-5,-17 L-3,-9 "
    "C-10,-11 -15,-17 -24,-20 L-39,-19 L-31,-12 L-45,-7 L-35,-2 "
    "L-43,5 L-31,4 L-26,12 L-18,7 L-12,14 L-7,5 "
    "C-6,10 -4,14 0,18 C4,14 6,10 7,5 "
    "L12,14 L18,7 L26,12 L31,4 L43,5 L35,-2 L45,-7 L31,-12 "
    "L39,-19 L24,-20 C15,-17 10,-11 3,-9 L5,-17 Z"
)


def realistic_bat(scale):
    """Static reusable bat silhouette; motion is animated by the parent group."""
    return f'<path d="{BAT_PATH}" transform="scale({scale:.2f})"/>'


def bat_swarm(theme):
    # 24 bats with only motion + opacity animations per bat.
    # This cuts the animation workload versus the old independently flapping wings.
    flights = [
        ("0.00s", "2.20s", "M-35,58 C170,5 350,28 545,86 C735,142 900,110 1030,30"),
        ("0.03s", "2.35s", "M-28,92 C155,28 338,45 520,105 C705,166 885,132 1035,58"),
        ("0.06s", "2.50s", "M-32,128 C160,55 345,70 530,132 C720,194 890,162 1032,86"),
        ("0.09s", "2.25s", "M-30,166 C170,92 355,105 538,164 C725,225 895,195 1038,120"),
        ("0.12s", "2.40s", "M-35,208 C175,132 365,145 548,205 C735,263 900,232 1032,160"),
        ("0.15s", "2.55s", "M-32,250 C180,176 370,188 555,248 C742,306 905,278 1030,205"),
        ("0.18s", "2.65s", "M-30,294 C185,220 378,232 563,290 C750,347 910,320 1032,245"),
        ("0.21s", "2.35s", "M-34,338 C195,265 390,278 575,335 C760,392 915,365 1035,292"),
        ("0.24s", "2.20s", "M-30,382 C205,312 402,322 590,378 C775,433 920,410 1032,340"),
        ("0.27s", "2.45s", "M-32,426 C215,360 418,368 605,420 C790,472 925,450 1030,388"),
        ("0.30s", "2.30s", "M-30,468 C225,405 430,412 618,463 C800,512 930,492 1028,435"),
        ("0.33s", "2.55s", "M-28,505 C235,452 445,456 632,500 C810,542 940,525 1032,478"),
        ("0.02s", "2.30s", "M1025,62 C830,10 650,38 470,104 C295,168 130,148 -45,55"),
        ("0.05s", "2.45s", "M1032,100 C835,45 655,70 475,136 C298,201 125,178 -48,86"),
        ("0.08s", "2.20s", "M1030,138 C838,80 660,105 480,170 C300,235 120,208 -45,118"),
        ("0.11s", "2.35s", "M1035,178 C842,120 665,142 485,207 C302,271 118,245 -48,155"),
        ("0.14s", "2.50s", "M1030,220 C845,163 670,184 490,247 C305,311 115,286 -45,198"),
        ("0.17s", "2.60s", "M1032,264 C848,208 675,228 495,291 C308,354 112,330 -48,242"),
        ("0.20s", "2.40s", "M1030,310 C850,255 678,274 500,336 C310,398 110,375 -45,288"),
        ("0.23s", "2.25s", "M1035,356 C852,302 680,320 502,381 C312,442 108,420 -48,334"),
        ("0.26s", "2.45s", "M1030,402 C848,350 675,367 498,426 C310,486 110,465 -45,380"),
        ("0.29s", "2.35s", "M1032,446 C845,398 668,414 492,470 C305,526 115,508 -48,425"),
        ("0.32s", "2.50s", "M1028,486 C838,444 660,456 485,506 C300,557 122,540 -45,465"),
        ("0.35s", "2.65s", "M1025,520 C830,486 650,494 475,536 C290,580 130,565 -42,500"),
    ]

    pieces = [f'<g fill="{theme["ascii"]}" pointer-events="none">']
    for index, (begin, duration, path) in enumerate(flights):
        scale = 0.34 + (index % 6) * 0.045
        opacity = 0.18 + (index % 4) * 0.025
        pieces.append(
            '<g opacity="0">'
            f'{realistic_bat(scale)}'
            f'<animate attributeName="opacity" values="0;{opacity:.2f};{opacity:.2f};0" '
            f'keyTimes="0;0.06;0.88;1" begin="{begin}" dur="{duration}" '
            f'calcMode="linear" repeatCount="1" fill="freeze"/>'
            f'<animateMotion path="{path}" begin="{begin}" dur="{duration}" '
            f'calcMode="paced" repeatCount="1" fill="freeze" rotate="auto"/>'
            '</g>'
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
