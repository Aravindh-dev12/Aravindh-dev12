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
    "                        _==/          i     i          \\==_                        ",
    "                      /XX/            |\\___/|            \\XX\\                      ",
    "                    /XXXX\\            |XXXXX|            /XXXX\\                    ",
    "                   |XXXXXX\\_         _/XXXXX\\_         _/XXXXXX|                   ",
    "                  XXXXXXXXXXXxxxxxxxXXXXXXXXXXXxxxxxxxXXXXXXXXXXX                  ",
    "                 |XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX|                 ",
    "                 XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX                 ",
    "                 |XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX|                 ",
    "                  XXXXXX/^^^^\\XXXXXXXXXXXXXXXXXXXXX/^^^^\\XXXXXX                  ",
    "                   |XXX|       \\XXX/^^\\XXXXX/^^\\XXX/       |XXX|                   ",
    "                    \\XX\\       \\X/    \\XXX/    \\X/       /XX/                    ",
    "                      '\\        '      \\X/      '        /'                      ",
    "                        '\\_                    __/                               ",
    "                           '====__________===='                                  ",
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

RIGHT_LABEL_X = 390
RIGHT_COLON_X = 545
RIGHT_DOTS_X = 558
RIGHT_VALUE_X = 590


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


def row(y, label, value, element_id=None):
    safe_label = html.escape(label)
    safe_value = html.escape(fmt(value))
    value_id = f' id="{element_id}"' if element_id else ""
    return (
        f'<tspan x="{RIGHT_LABEL_X}" y="{y}" class="cc">. </tspan>'
        f'<tspan class="key">{safe_label}</tspan>'
        f'<tspan x="{RIGHT_COLON_X}" y="{y}" class="cc">:</tspan>'
        f'<tspan x="{RIGHT_DOTS_X}" y="{y}" class="cc">....................</tspan>'
        f'<tspan x="{RIGHT_VALUE_X}" y="{y}" class="value"{value_id}>{safe_value}</tspan>'
    )


def render_svg(theme_name, stats):
    t = THEMES[theme_name]

    ascii_lines = "\n".join(
        f'<tspan x="24" y="{50 + i * 27}">{html.escape(line)}</tspan>'
        for i, line in enumerate(BATMAN_ASCII)
    )

    profile_lines = "\n".join([
        row(50, "Role", "AI Builder · Full-Stack Developer"),
        row(78, "Focus", "LLM · RAG · Agents · Web · Flutter"),
        row(106, "Stack", "Python · TypeScript · Dart · GitHub"),
        row(134, "Status", "Building · Learning · Shipping"),
    ])

    focus_lines = "\n".join([
        row(194, "AI", "LLM systems · RAG · agent workflows"),
        row(222, "Apps", "Web products · Flutter · automation"),
        row(250, "Research", "Neuro-symbolic · inference · retrieval"),
        row(278, "Mode", "Build in the shadows. Ship in the light."),
    ])

    activity_lines = "\n".join([
        row(334, "Contributions", stats["contrib_data"], "contrib_data"),
        row(362, "Current Streak", stats["streak_data"], "streak_data"),
        row(390, "Commits", stats["commit_data"], "commit_data"),
        row(418, "Pull Requests", stats["pr_data"], "pr_data"),
        row(446, "Reviews", stats["review_data"], "review_data"),
        row(474, "Issues", stats["issue_data"], "issue_data"),
        row(502, "Active Days", stats["active_data"], "active_data"),
        row(530, "Followers", stats["follower_data"], "follower_data"),
        row(558, "Last Refresh", stats["updated_data"], "updated_data"),
    ])

    footer_lines = "\n".join([
        row(614, "Signal", "The code is the signal."),
        row(642, "Handle", "@Aravindh-dev12"),
    ])

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="680px" font-size="16px" role="img" aria-label="Aravindhan Batman GitHub profile card">
<style>
@font-face {{ src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback'; font-display: swap; -webkit-size-adjust: 109%; size-adjust: 109%; }}
.key {{fill: {t['key']}; font-weight: 700;}}
.value {{fill: {t['value']};}}
.cc {{fill: {t['muted']};}}
text, tspan {{white-space: pre;}}
</style>

<rect width="985px" height="680px" fill="{t['background']}" rx="15"/>

<!-- Border only around the Batman symbol -->
<rect x="16" y="18" width="342" height="410" rx="12" fill="none" stroke="{t['muted']}" stroke-width="1.2" opacity="0.60"/>

<text x="24" y="50" fill="{t['ascii']}" class="ascii" font-size="12px">
{ascii_lines}
</text>

<text x="{RIGHT_LABEL_X}" y="30" fill="{t['text']}">
<tspan x="{RIGHT_LABEL_X}" y="30">aravindhan@batcave</tspan> -——————————————————————————————————————————————
{profile_lines}

<tspan x="{RIGHT_LABEL_X}" y="166">- Current Focus</tspan> -———————————————————————————————————————————————
{focus_lines}

<tspan x="{RIGHT_LABEL_X}" y="306">- GitHub Activity · rolling 365 days</tspan> -——————————————————————————————
{activity_lines}

{footer_lines}
</text>
</svg>'''


def render_readme(cache_stamp):
    return f'''<!-- daily-refresh: {cache_stamp} -->
<div align="center">
  <a href="https://github.com/{USER_NAME}">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/{USER_NAME}/{USER_NAME}/main/dark_mode.svg?v={cache_stamp}">
      <img width="100%" alt="Aravindhan's Batman developer profile with daily GitHub activity" src="https://raw.githubusercontent.com/{USER_NAME}/{USER_NAME}/main/light_mode.svg?v={cache_stamp}">
    </picture>
  </a>

  <p><em>"It's not who I am underneath, but what I do that defines me."</em></p>
  <sub>— Batman Begins</sub>
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
