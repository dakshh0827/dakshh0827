import os
import html


OUTPUT = "info-card.svg"

WIDTH = 490
HEIGHT = 370

BACKGROUND = "#0d1117"
BORDER = "#30363d"

TEXT = "#c9d1d9"
MUTED = "#8b949e"

GREEN = "#39d353"
BLUE = "#58a6ff"
PURPLE = "#bc8cff"
ORANGE = "#f0883e"

FONT = "monospace"

STATIC = os.environ.get("STATIC") == "1"


# ============================================================
# SPEED
# ============================================================

# Same terminal-style speed as the ASCII portrait.
CHAR_DELAY = 0.010

# Pause after each completed line.
LINE_PAUSE = 0.06


# ============================================================
# CONTENT
# ============================================================

rows = [
    (
        "Now",
        "Building and running!",
        GREEN
    ),
    (
        "Prev",
        "Full-stack development",
        BLUE
    ),
    (
        "Stack",
        "Java · React · Node.js · MongoDB",
        PURPLE
    ),
    (
        "Focus",
        "DSA · Backend · System Design",
        ORANGE
    ),
    (
        "Build",
        "Agentra · Wrap-Up · MaViK-39",
        GREEN
    ),
    (
        "Status",
        "Open to anything!",
        BLUE
    ),
]


# ============================================================
# SVG START
# ============================================================

svg = []

svg.append(
    f'''<svg
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
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="12"
    fill="{BACKGROUND}"
    stroke="{BORDER}"
/>
'''
)


# ============================================================
# TERMINAL TITLE BAR
# ============================================================

svg.append(
    '<circle cx="22" cy="22" r="5" fill="#ff5f56"/>'
)

svg.append(
    '<circle cx="40" cy="22" r="5" fill="#ffbd2e"/>'
)

svg.append(
    '<circle cx="58" cy="22" r="5" fill="#27c93f"/>'
)


svg.append(
    f'''
<text
    x="{WIDTH / 2}"
    y="27"
    text-anchor="middle"
    font-family="{FONT}"
    font-size="12"
    fill="{MUTED}">
    daksh@github:~
</text>
'''
)


svg.append(
    f'''
<line
    x1="0"
    y1="43"
    x2="{WIDTH}"
    y2="43"
    stroke="{BORDER}"
/>
'''
)


# ============================================================
# CHARACTER HELPER
# ============================================================

CHAR_WIDTH = 7.8
FONT_SIZE = 13

current_time = 0.15


def add_character(
    char,
    x,
    y,
    color,
    bold=False,
    delay=None
):
    if char == " ":
        return

    escaped = html.escape(char)

    weight = (
        'font-weight="bold"'
        if bold
        else ""
    )

    if STATIC:

        svg.append(
            f'''
<text
    x="{x:.2f}"
    y="{y}"
    fill="{color}"
    font-family="{FONT}"
    font-size="{FONT_SIZE}px"
    {weight}>{escaped}</text>
'''
        )

    else:

        svg.append(
            f'''
<text
    x="{x:.2f}"
    y="{y}"
    fill="{color}"
    font-family="{FONT}"
    font-size="{FONT_SIZE}px"
    {weight}
    opacity="0">{escaped}

    <set
        attributeName="opacity"
        to="1"
        begin="{delay:.4f}s"
        fill="freeze"
    />

</text>
'''
        )


# ============================================================
# HEADER
# ============================================================

header = "dakshh0827@github"

HEADER_Y = 78
HEADER_X = 25


for col, char in enumerate(header):

    x = (
        HEADER_X
        + col * CHAR_WIDTH
    )

    add_character(
        char,
        x,
        HEADER_Y,
        GREEN,
        bold=True,
        delay=current_time
    )

    current_time += CHAR_DELAY


current_time += LINE_PAUSE


# ============================================================
# DIVIDER
# ============================================================

divider = "------------------------------"

DIVIDER_Y = 100


for col, char in enumerate(divider):

    x = (
        HEADER_X
        + col * CHAR_WIDTH
    )

    add_character(
        char,
        x,
        DIVIDER_Y,
        MUTED,
        delay=current_time
    )

    current_time += CHAR_DELAY


current_time += LINE_PAUSE


# ============================================================
# INFORMATION ROWS
# ============================================================

START_Y = 135
ROW_HEIGHT = 35


for row_index, (key, value, key_color) in enumerate(rows):

    y = (
        START_Y
        + row_index * ROW_HEIGHT
    )

    # Pad keys so values line up.
    key_text = key.ljust(7)

    line_position = 0


    # --------------------------------------------------------
    # KEY
    # --------------------------------------------------------

    for char in key_text:

        x = (
            HEADER_X
            + line_position * CHAR_WIDTH
        )

        add_character(
            char,
            x,
            y,
            key_color,
            bold=True,
            delay=current_time
        )

        current_time += CHAR_DELAY
        line_position += 1


    # --------------------------------------------------------
    # COLON
    # --------------------------------------------------------

    for char in ": ":

        x = (
            HEADER_X
            + line_position * CHAR_WIDTH
        )

        add_character(
            char,
            x,
            y,
            TEXT,
            delay=current_time
        )

        current_time += CHAR_DELAY
        line_position += 1


    # --------------------------------------------------------
    # VALUE
    # --------------------------------------------------------

    for char in value:

        x = (
            HEADER_X
            + line_position * CHAR_WIDTH
        )

        add_character(
            char,
            x,
            y,
            TEXT,
            delay=current_time
        )

        current_time += CHAR_DELAY
        line_position += 1


    current_time += LINE_PAUSE


# ============================================================
# CURSOR
# ============================================================

if not STATIC:

    cursor_time = 0.15


    # --------------------------------------------------------
    # Header cursor
    # --------------------------------------------------------

    lines = []

    lines.append(
        (
            header,
            HEADER_X,
            HEADER_Y
        )
    )

    lines.append(
        (
            divider,
            HEADER_X,
            DIVIDER_Y
        )
    )


    for row_index, (key, value, color) in enumerate(rows):

        line = (
            key.ljust(7)
            + ": "
            + value
        )

        y = (
            START_Y
            + row_index * ROW_HEIGHT
        )

        lines.append(
            (
                line,
                HEADER_X,
                y
            )
        )


    for line, start_x, y in lines:

        for col in range(len(line)):

            x = (
                start_x
                + col * CHAR_WIDTH
            )

            start = cursor_time
            end = (
                cursor_time
                + CHAR_DELAY
            )


            svg.append(
                f'''
<rect
    x="{x:.2f}"
    y="{y - 13}"
    width="6"
    height="15"
    fill="{TEXT}"
    opacity="0">

    <set
        attributeName="opacity"
        to="1"
        begin="{start:.4f}s"
    />

    <set
        attributeName="opacity"
        to="0"
        begin="{end:.4f}s"
    />

</rect>
'''
            )


            cursor_time += CHAR_DELAY


        cursor_time += LINE_PAUSE


# ============================================================
# SAVE
# ============================================================

svg.append("</svg>")


with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(svg)
    )


print()
print("Info card generated")
print("-------------------")
print(f"Output: {OUTPUT}")
print(
    f"Animation length: {current_time:.2f}s"
)

if STATIC:
    print("Mode: STATIC")
else:
    print("Mode: TRUE CHARACTER TYPEWRITER")

print()