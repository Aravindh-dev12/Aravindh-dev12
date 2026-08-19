import datetime as dt
import os
import re
from pathlib import Path

import requests
from lxml import etree

USER_NAME = os.getenv("USER_NAME", "Aravindh-dev12")
TOKEN = os.getenv("ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
GRAPHQL_URL = "https://api.github.com/graphql"

SVG_FILES = ("dark_mode.svg", "light_mode.svg")
README_FILE = Path("README.md")


def github_activity():
    now = dt.datetime.now(dt.timezone.utc)
    start = now - dt.timedelta(days=364)

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
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

    collection = payload["data"]["user"]["contributionsCollection"]
    calendar = collection["contributionCalendar"]
    days = [
        day
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]

    active_days = sum(1 for day in days if day["contributionCount"] > 0)
    streak = current_streak(days)

    return {
        "contrib_data": calendar["totalContributions"],
        "streak_data": f"{streak} day" + ("" if streak == 1 else "s"),
        "commit_data": collection["totalCommitContributions"],
        "pr_data": collection["totalPullRequestContributions"],
        "review_data": collection["totalPullRequestReviewContributions"],
        "issue_data": collection["totalIssueContributions"],
        "active_data": active_days,
        "updated_data": now.strftime("%Y-%m-%d UTC"),
    }


def current_streak(days):
    if not days:
        return 0

    ordered = sorted(days, key=lambda d: d["date"])
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()

    index = len(ordered) - 1
    while index >= 0 and ordered[index]["date"] > today:
        index -= 1

    # Keep an active streak alive through the current day if today's count is still zero.
    if index >= 0 and ordered[index]["date"] == today and ordered[index]["contributionCount"] == 0:
        index -= 1

    streak = 0
    while index >= 0 and ordered[index]["contributionCount"] > 0:
        streak += 1
        index -= 1
    return streak


def set_text(root, element_id, value):
    element = root.find(f".//*[@id='{element_id}']")
    if element is None:
        return
    if isinstance(value, int):
        value = f"{value:,}"
    element.text = str(value)

    dots = root.find(f".//*[@id='{element_id}_dots']")
    if dots is not None:
        width = 21
        visible_len = len(str(value))
        dots.text = " " + "." * max(3, width - visible_len) + " "


def update_svg(filename, stats):
    tree = etree.parse(filename)
    root = tree.getroot()
    for key, value in stats.items():
        set_text(root, key, value)
    tree.write(filename, encoding="utf-8", xml_declaration=True)


def update_readme_cache_buster():
    if not README_FILE.exists():
        return

    text = README_FILE.read_text(encoding="utf-8")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")

    if "<!-- daily-refresh:" in text:
        text = re.sub(r"<!-- daily-refresh: .*? -->", f"<!-- daily-refresh: {stamp} -->", text)
    else:
        text = f"<!-- daily-refresh: {stamp} -->\n" + text

    text = re.sub(r"(dark_mode\.svg)(?:\?v=[^\"']+)?", rf"\1?v={stamp}", text)
    text = re.sub(r"(light_mode\.svg)(?:\?v=[^\"']+)?", rf"\1?v={stamp}", text)
    README_FILE.write_text(text, encoding="utf-8")


def main():
    stats = github_activity()
    for svg in SVG_FILES:
        update_svg(svg, stats)
    update_readme_cache_buster()
    print("Updated profile activity:", stats)


if __name__ == "__main__":
    main()
