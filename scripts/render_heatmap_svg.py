import json
import html
from datetime import datetime
from pathlib import Path


INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")


PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]


WIDTH = 860
HEIGHT = 190

CELL = 11
GAP = 3

GRID_X = 55
GRID_Y = 35

TEXT = "#8b949e"
BRIGHT_TEXT = "#c9d1d9"
BACKGROUND = "#0d1117"


data = json.loads(
    INPUT.read_text(encoding="utf-8")
)

days = data["days"]
stats = data["stats"]


# ----------------------------------
# Organize contributions by date
# ----------------------------------

by_date = {
    d["date"]: d
    for d in days
}


dates = sorted(
    datetime.strptime(d["date"], "%Y-%m-%d").date()
    for d in days
)


first = dates[0]

# Move back to Sunday
start = first

while start.weekday() != 6:
    from datetime import timedelta
    start -= timedelta(days=1)


svg = []

svg.append(
    f'''
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">
'''
)


svg.append(
    f'''
<rect
    width="100%"
    height="100%"
    rx="12"
    fill="{BACKGROUND}"
/>
'''
)


# ----------------------------------
# CSS animation
# ----------------------------------

svg.append(
    '''
<style>

.day {
    opacity: 0;
    transform: translateY(-8px);
    animation: reveal .4s ease forwards;
}

@keyframes reveal {

    from {
        opacity: 0;
        transform: translateY(-8px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }

}

</style>
'''
)


# ----------------------------------
# Day labels
# ----------------------------------

labels = [
    ("Mon", 1),
    ("Wed", 3),
    ("Fri", 5)
]

for label, row in labels:

    y = GRID_Y + row * (CELL + GAP) + 9

    svg.append(
        f'''
<text
    x="12"
    y="{y}"
    fill="{TEXT}"
    font-family="monospace"
    font-size="10">
    {label}
</text>
'''
    )


# ----------------------------------
# Contribution cells
# ----------------------------------

from datetime import timedelta


current = start

end = dates[-1]

week = 0


while current <= end:

    weekday = (
        current.weekday() + 1
    ) % 7

    key = current.isoformat()

    info = by_date.get(
        key,
        {
            "count": 0,
            "level": 0
        }
    )

    level = min(
        int(info["level"]),
        len(PALETTE) - 1
    )

    count = info["count"]

    x = GRID_X + week * (CELL + GAP)

    y = GRID_Y + weekday * (CELL + GAP)

    delay = (
        week * 0.015
        + weekday * 0.025
    )

    color = PALETTE[level]

    svg.append(
        f'''
<rect
    class="day"
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    rx="2"
    fill="{color}"
    style="animation-delay:{delay:.3f}s">

    <title>
        {count} contributions on {key}
    </title>

</rect>
'''
    )

    current += timedelta(days=1)

    if weekday == 6:
        week += 1


# ----------------------------------
# Legend
# ----------------------------------

legend_y = 155

svg.append(
    f'''
<text
    x="560"
    y="{legend_y + 10}"
    fill="{TEXT}"
    font-family="monospace"
    font-size="10">
    Less
</text>
'''
)


legend_x = 600

for i, color in enumerate(PALETTE):

    x = legend_x + i * 16

    svg.append(
        f'''
<rect
    x="{x}"
    y="{legend_y}"
    width="11"
    height="11"
    rx="2"
    fill="{color}"
/>
'''
    )


svg.append(
    f'''
<text
    x="{legend_x + len(PALETTE) * 16 + 3}"
    y="{legend_y + 10}"
    fill="{TEXT}"
    font-family="monospace"
    font-size="10">
    More
</text>
'''
)


# ----------------------------------
# Statistics
# ----------------------------------

total = stats["total"]
current_streak = stats["current_streak"]
longest = stats["longest_streak"]


svg.append(
    f'''
<text
    x="55"
    y="165"
    fill="{BRIGHT_TEXT}"
    font-family="monospace"
    font-size="11">
    {total:,} contributions ·
    current streak {current_streak} days ·
    longest streak {longest} days
</text>
'''
)


svg.append("</svg>")


OUTPUT.write_text(
    "\n".join(svg),
    encoding="utf-8"
)


print(f"Generated {OUTPUT}")
