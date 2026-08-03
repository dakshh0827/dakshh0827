import json
import os

from datetime import datetime, timedelta
from pathlib import Path


INPUT = Path(
    "data/contributions.json"
)

OUTPUT = Path(
    "contrib-heatmap.svg"
)


# ============================================================
# APPEARANCE
# ============================================================

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

STATIC = os.environ.get("STATIC") == "1"


# ============================================================
# TYPEWRITER SPEED
# ============================================================

# Delay between individual contribution squares.
CELL_DELAY = 0.012

# Pause after one complete horizontal row.
ROW_PAUSE = 0.05


# ============================================================
# LOAD DATA
# ============================================================

data = json.loads(
    INPUT.read_text(
        encoding="utf-8"
    )
)

days = data["days"]
stats = data["stats"]


# ============================================================
# DATE MAP
# ============================================================

by_date = {
    day["date"]: day
    for day in days
}


dates = sorted(
    datetime.strptime(
        day["date"],
        "%Y-%m-%d"
    ).date()
    for day in days
)


if not dates:

    raise RuntimeError(
        "No contribution dates found."
    )


first = dates[0]
last = dates[-1]


# ============================================================
# FIND STARTING SUNDAY
# ============================================================

start = first

while start.weekday() != 6:

    start -= timedelta(
        days=1
    )


# ============================================================
# BUILD CALENDAR GRID
# ============================================================

weeks = []


current = start


while current <= last:

    days_since_start = (
        current - start
    ).days

    week_index = (
        days_since_start // 7
    )


    while len(weeks) <= week_index:

        weeks.append(
            [None] * 7
        )


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


    weeks[week_index][weekday] = {
        "date": key,
        "count": int(
            info.get(
                "count",
                0
            )
        ),
        "level": int(
            info.get(
                "level",
                0
            )
        )
    }


    current += timedelta(
        days=1
    )


# ============================================================
# SVG START
# ============================================================

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


# ============================================================
# BACKGROUND
# ============================================================

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


# ============================================================
# WEEKDAY LABELS
# ============================================================

labels = [
    ("Mon", 1),
    ("Wed", 3),
    ("Fri", 5)
]


for label, row in labels:

    y = (
        GRID_Y
        + row * (CELL + GAP)
        + 9
    )


    svg.append(
        f'''
<text
    x="12"
    y="{y}"
    fill="{TEXT}"
    font-family="monospace"
    font-size="10">{label}</text>
'''
    )


# ============================================================
# TRUE ROW-BY-ROW CELL PRINTING
#
# IMPORTANT:
#
# We iterate:
#
#     row
#       ↓
#     column
#
# NOT:
#
#     week
#       ↓
#     weekday
#
# Therefore:
#
# row 0:
#   col 0 -> col 52
#
# THEN row 1:
#   col 0 -> col 52
#
# etc.
# ============================================================

current_time = 0.15


for row in range(7):

    for week_index in range(
        len(weeks)
    ):

        cell_info = (
            weeks[week_index][row]
        )


        # Some edge cells may be outside
        # GitHub's returned date range.
        if cell_info is None:

            current_time += CELL_DELAY
            continue


        level = min(
            cell_info["level"],
            len(PALETTE) - 1
        )


        count = (
            cell_info["count"]
        )

        date = (
            cell_info["date"]
        )


        color = (
            PALETTE[level]
        )


        x = (
            GRID_X
            + week_index
            * (CELL + GAP)
        )


        y = (
            GRID_Y
            + row
            * (CELL + GAP)
        )


        if STATIC:

            svg.append(
                f'''
<rect
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    rx="2"
    fill="{color}">

    <title>{count} contributions on {date}</title>

</rect>
'''
            )

        else:

            svg.append(
                f'''
<rect
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    rx="2"
    fill="{color}"
    opacity="0">

    <title>{count} contributions on {date}</title>

    <set
        attributeName="opacity"
        to="1"
        begin="{current_time:.4f}s"
        fill="freeze"
    />

</rect>
'''
            )


        current_time += CELL_DELAY


    # Finished this horizontal row.
    current_time += ROW_PAUSE


# ============================================================
# CELL CURSOR
# ============================================================

if not STATIC:

    cursor_time = 0.15


    for row in range(7):

        for week_index in range(
            len(weeks)
        ):

            x = (
                GRID_X
                + week_index
                * (CELL + GAP)
            )


            y = (
                GRID_Y
                + row
                * (CELL + GAP)
            )


            start_time = cursor_time

            end_time = (
                cursor_time
                + CELL_DELAY
            )


            svg.append(
                f'''
<rect
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    rx="2"
    fill="{BRIGHT_TEXT}"
    opacity="0">

    <set
        attributeName="opacity"
        to="0.75"
        begin="{start_time:.4f}s"
    />

    <set
        attributeName="opacity"
        to="0"
        begin="{end_time:.4f}s"
    />

</rect>
'''
            )


            cursor_time += CELL_DELAY


        cursor_time += ROW_PAUSE


# ============================================================
# LEGEND
# ============================================================

legend_y = 145
legend_x = 620


svg.append(
    f'''
<text
    x="{legend_x - 38}"
    y="{legend_y + 10}"
    fill="{TEXT}"
    font-family="monospace"
    font-size="10">
    Less
</text>
'''
)


for i, color in enumerate(
    PALETTE
):

    x = (
        legend_x
        + i * 16
    )


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


more_x = (
    legend_x
    + len(PALETTE) * 16
    + 3
)


svg.append(
    f'''
<text
    x="{more_x}"
    y="{legend_y + 10}"
    fill="{TEXT}"
    font-family="monospace"
    font-size="10">
    More
</text>
'''
)


# ============================================================
# STATISTICS
# ============================================================

total = int(
    stats.get(
        "total",
        0
    )
)

current_streak = int(
    stats.get(
        "current_streak",
        0
    )
)

longest = int(
    stats.get(
        "longest_streak",
        0
    )
)


footer = (
    f"{total:,} contributions"
    f" · current streak {current_streak} days"
    f" · longest streak {longest} days"
)


# ============================================================
# TYPE FOOTER CHARACTER-BY-CHARACTER
# ============================================================

FOOTER_X = GRID_X
FOOTER_Y = 165

FOOTER_CHAR_WIDTH = 6.6
FOOTER_CHAR_DELAY = 0.010


for index, char in enumerate(
    footer
):

    x = (
        FOOTER_X
        + index * FOOTER_CHAR_WIDTH
    )


    if char == " ":

        current_time += (
            FOOTER_CHAR_DELAY
        )

        continue


    if STATIC:

        svg.append(
            f'''
<text
    x="{x:.2f}"
    y="{FOOTER_Y}"
    fill="{BRIGHT_TEXT}"
    font-family="monospace"
    font-size="11">{char}</text>
'''
        )

    else:

        svg.append(
            f'''
<text
    x="{x:.2f}"
    y="{FOOTER_Y}"
    fill="{BRIGHT_TEXT}"
    font-family="monospace"
    font-size="11"
    opacity="0">{char}

    <set
        attributeName="opacity"
        to="1"
        begin="{current_time:.4f}s"
        fill="freeze"
    />

</text>
'''
        )


    current_time += (
        FOOTER_CHAR_DELAY
    )


# ============================================================
# SAVE
# ============================================================

svg.append("</svg>")


OUTPUT.write_text(
    "\n".join(svg),
    encoding="utf-8"
)


print()
print("Contribution heatmap generated")
print("------------------------------")

print(
    f"Weeks: {len(weeks)}"
)

print(
    f"Animation length: {current_time:.2f}s"
)

print(
    f"Output: {OUTPUT}"
)

if STATIC:
    print("Mode: STATIC")
else:
    print("Mode: TRUE ROW-BY-ROW TYPEWRITER")

print()