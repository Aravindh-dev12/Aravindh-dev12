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
BAT_PATH = "M0 5 L4 1 L8 4 L12 0 L16 4 L20 1 L24 5 L19 6 L16 10 L12 7 L8 10 L5 6 Z"


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


def bat_swarm(theme):
    flights = [
        ("-0.2s", "6.1s", "M18,92 C190,20 385,10 575,70 C760,128 900,90 975,32"),
        ("-1.1s", "7.0s", "M15,170 C170,75 355,48 540,118 C720,185 880,162 978,85"),
        ("-2.0s", "6.6s", "M22,270 C175,175 345,155 540,215 C735,275 890,250 975,170"),
        ("-2.9s", "7.4s", "M16,380 C185,288 365,270 555,330 C745,390 885,362 972,285"),
        ("-3.8s", "6.8s", "M25,485 C210,405 400,395 585,445 C760,492 900,470 972,400"),
        ("-0.7s", "5.8s", "M965,75 C790,20 620,40 465,110 C310,178 155,155 28,72"),
        ("-1.6s", "6.4s", "M970,155 C790,95 625,125 470,190 C300,262 145,228 20,145"),
        ("-2.5s", "7.2s", "M972,255 C810,205 650,225 482,290 C315,355 150,333 20,255"),
        ("-3.4s", "6.0s", "M970,355 C810,315 650,335 485,395 C310,458 150,435 18,350"),
        ("-4.3s", "7.6s", "M968,455 C800,420 635,425 475,470 C310,515 145,505 22,438"),
        ("-0.4s", "6.9s", "M105,515 C65,390 95,250 205,155 C320,55 500,12 690,42 C835,65 930,145 980,245"),
        ("-1.3s", "7.8s", "M250,520 C155,420 145,280 245,165 C355,40 540,5 725,58 C870,100 950,205 975,320"),
        ("-2.2s", "6.3s", "M410,520 C285,455 240,325 315,205 C395,75 570,20 750,72 C895,115 960,225 970,350"),
        ("-3.1s", "7.1s", "M565,520 C420,480 340,365 390,235 C440,105 595,35 770,88 C900,128 965,238 968,385"),
        ("-4.0s", "6.5s", "M720,510 C565,500 450,405 455,275 C460,135 600,55 790,105 C915,140 970,250 960,410"),
        ("-0.9s", "7.3s", "M885,500 C720,505 570,430 550,300 C530,165 650,70 825,115 C945,150 980,270 950,425"),
        ("-1.8s", "5.9s", "M40,35 C175,145 255,235 220,345 C188,455 315,520 480,500 C650,480 725,385 700,280 C675,175 790,85 955,28"),
        ("-2.7s", "6.7s", "M25,505 C165,420 230,335 205,245 C175,135 315,35 495,42 C685,50 775,155 750,260 C725,365 820,445 965,500"),
        ("-3.6s", "7.5s", "M20,225 C155,120 320,80 485,130 C650,182 805,135 972,45"),
        ("-4.5s", "6.2s", "M18,330 C170,245 335,218 500,265 C670,312 820,280 974,195"),
        ("-0.5s", "7.7s", "M135,20 C210,135 350,175 495,125 C645,72 810,125 935,245"),
        ("-1.4s", "6.6s", "M330,18 C355,145 470,205 605,165 C750,120 875,190 960,315"),
        ("-2.3s", "7.0s", "M600,20 C555,145 650,225 770,235 C890,245 950,330 968,465"),
        ("-3.2s", "6.4s", "M820,22 C720,115 705,225 805,300 C900,372 925,430 900,515"),
    ]

    pieces = [f'<g fill="{theme["ascii"]}" opacity="0.78" pointer-events="none">']
    for index, (begin, duration, path) in enumerate(flights):
        scale = 0.72 + (index % 6) * 0.10
        pieces.append(
            f'<g>'
            f'<path d="{BAT_PATH}" transform="scale({scale:.2f})"/>'
            f'<animateMotion path="{path}" begin="{begin}" dur="{duration}" '
            f'repeatCount="indefinite" rotate="auto"/>'
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
