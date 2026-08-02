import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "dakshh0827"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT = Path("data/contributions.json")


def fetch():
    print(f"Fetching contributions for {USERNAME}...")

    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.text


def parse_count(text):
    """
    Examples GitHub may return:

    '12 contributions on August 1st.'
    '1 contribution on August 1st.'
    'No contributions on August 1st.'
    """

    if not text:
        return 0

    text = text.strip()

    if text.lower().startswith("no contributions"):
        return 0

    match = re.search(
        r"(\d[\d,]*)\s+contribution",
        text,
        re.IGNORECASE,
    )

    if match:
        return int(
            match.group(1).replace(",", "")
        )

    return 0


def parse(html):
    soup = BeautifulSoup(html, "html.parser")

    days = []

    cells = soup.select(
        "td.ContributionCalendar-day[data-date][data-level]"
    )

    print(f"Found {len(cells)} calendar cells")

    for cell in cells:
        date = cell.get("data-date")

        level = int(
            cell.get("data-level", 0)
        )

        count = 0

        # ------------------------------------------------
        # GitHub associates each calendar cell with
        # accessible descriptive text elsewhere in HTML.
        # ------------------------------------------------

        cell_id = cell.get("id")

        description = None

        if cell_id:
            # Look for elements referring to this cell.
            candidates = soup.find_all(
                attrs={
                    "for": cell_id
                }
            )

            if candidates:
                description = candidates[0].get_text(
                    " ",
                    strip=True
                )

        # ------------------------------------------------
        # Current GitHub markup commonly places the
        # accessible count in a tooltip element whose
        # relationship can vary.
        # ------------------------------------------------

        if not description and cell_id:
            candidate = soup.find(
                id=f"{cell_id}-tooltip"
            )

            if candidate:
                description = candidate.get_text(
                    " ",
                    strip=True
                )

        # ------------------------------------------------
        # Last fallback:
        # search nearby text for the date.
        # ------------------------------------------------

        if not description:

            parent = cell.parent

            if parent:
                nearby = parent.get_text(
                    " ",
                    strip=True
                )

                if "contribution" in nearby.lower():
                    description = nearby

        count = parse_count(description)

        days.append({
            "date": date,
            "count": count,
            "level": level,
        })

    return days


def calculate_stats(days):
    days = sorted(
        days,
        key=lambda d: d["date"]
    )

    total = sum(
        d["count"]
        for d in days
    )

    # -----------------------------
    # Best day
    # -----------------------------

    best_day = max(
        days,
        key=lambda d: d["count"],
        default=None,
    )

    # -----------------------------
    # Longest streak
    # -----------------------------

    longest = 0
    streak = 0

    for day in days:

        if day["count"] > 0:
            streak += 1
            longest = max(
                longest,
                streak
            )
        else:
            streak = 0

    # -----------------------------
    # Current streak
    # -----------------------------

    current = 0

    # Ignore future dates if GitHub happens to include them.
    today = datetime.now(
        timezone.utc
    ).date().isoformat()

    past_days = [
        d for d in days
        if d["date"] <= today
    ]

    for day in reversed(past_days):

        if day["count"] > 0:
            current += 1
        else:
            break

    # -----------------------------
    # Monthly totals
    # -----------------------------

    monthly = {}

    for day in days:

        month = day["date"][:7]

        monthly[month] = (
            monthly.get(month, 0)
            + day["count"]
        )

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_totals": monthly,
    }


def main():
    html = fetch()

    days = parse(html)

    if not days:
        raise RuntimeError(
            "No contribution cells found."
        )

    stats = calculate_stats(days)

    data = {
        "username": USERNAME,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "days": days,
        "stats": stats,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Found {len(days)} days")
    print(
        f"Total contributions: "
        f"{stats['total']}"
    )
    print(
        f"Current streak: "
        f"{stats['current_streak']}"
    )
    print(
        f"Longest streak: "
        f"{stats['longest_streak']}"
    )

    if stats["best_day"]:
        print(
            "Best day:",
            stats["best_day"]["date"],
            "-",
            stats["best_day"]["count"],
        )

    print()
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()