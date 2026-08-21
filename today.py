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
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          restrictedContributionsCount
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
        "pr_data": collection["totalPullRequestContributions"],
        "review_data": collection["totalPullRequestReviewContributions"],
        "issue_data": collection["totalIssueContributions"],
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
        stat_line(346, "Pull Requests", "pr_data", stats["pr_data"]),
        stat_line(366, "Reviews", "review_data", stats["review_data"]),
        stat_line(386, "Issues", "issue_data", stats["issue_data"]),
        stat_line(406, "Active Days", "active_data", stats["active_data"]),
        stat_line(426, "Followers", "follower_data", stats["follower_data"]),
        stat_line(446, "Last Refresh", "updated_data", stats["updated_data"]),
    ])

    footer_lines = "\n".join([
        fixed_line(486, "Signal", "The code is the signal."),
        fixed_line(506, "Handle", "@Aravindh-dev12"),
    ])

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
