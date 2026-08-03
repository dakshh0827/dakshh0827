from PIL import Image
import html
import os


# ============================================================
# CONFIGURATION
# ============================================================

INPUT = "source-prepped.png"
OUTPUT = "avi-ascii.svg"

# ASCII grid width
COLS = 100

# Bright -> dark
# Leading space = white/background disappears
RAMP = " .`:-=+*cs#%@"

FONT_SIZE = 10
CHAR_WIDTH = 6
LINE_HEIGHT = 10

TEXT_COLOR = "#b8b8b8"
BACKGROUND = "#0d1117"

# ------------------------------------------------------------
# TYPEWRITER SPEED
# ------------------------------------------------------------

# Seconds between each CHARACTER
CHAR_DELAY = 0.001

# Small pause after finishing each ROW
ROW_PAUSE = 0.005

# Cursor size
CURSOR_WIDTH = 5

STATIC = os.environ.get("STATIC") == "1"


# ============================================================
# BRIGHTNESS -> ASCII
# ============================================================

def brightness_to_char(value):
    """
    255 = white -> space
    0   = black -> dense character
    """

    normalized = 1 - (value / 255.0)

    index = int(
        normalized * (len(RAMP) - 1)
    )

    return RAMP[index]


# ============================================================
# LOAD IMAGE
# ============================================================

img = Image.open(INPUT).convert("L")

aspect_ratio = img.height / img.width

# Correct for monospace character proportions
rows = max(
    1,
    int(
        COLS
        * aspect_ratio
        * 0.52
    )
)

img = img.resize(
    (COLS, rows)
)

pixels = img.load()


# ============================================================
# IMAGE -> ASCII GRID
# ============================================================

ascii_grid = []

for row in range(rows):

    characters = []

    for col in range(COLS):

        brightness = pixels[col, row]

        char = brightness_to_char(
            brightness
        )

        characters.append(char)

    ascii_grid.append(characters)


# ============================================================
# SVG DIMENSIONS
# ============================================================

WIDTH = COLS * CHAR_WIDTH
HEIGHT = rows * LINE_HEIGHT


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
    width="{WIDTH}"
    height="{HEIGHT}"
    fill="{BACKGROUND}"
/>
'''
)


# ============================================================
# ASCII CHARACTERS
#
# IMPORTANT:
#
# Every character is an INDIVIDUAL SVG <text>.
#
# There are NO:
#   clipPaths
#   masks
#   width animations
#
# Characters literally appear one at a time.
# ============================================================

current_time = 0.0


for row in range(rows):

    y = (
        row + 1
    ) * LINE_HEIGHT

    for col in range(COLS):

        char = ascii_grid[row][col]

        x = col * CHAR_WIDTH


        # ----------------------------------------------------
        # Spaces don't need to be rendered.
        #
        # But their typing time still passes so that character
        # positions remain correct.
        # ----------------------------------------------------

        if char != " ":

            escaped = html.escape(
                char
            )

            if STATIC:

                svg.append(
                    f'''
<text
    x="{x}"
    y="{y}"
    fill="{TEXT_COLOR}"
    font-family="monospace"
    font-size="{FONT_SIZE}px">{escaped}</text>
'''
                )

            else:

                svg.append(
                    f'''
<text
    x="{x}"
    y="{y}"
    fill="{TEXT_COLOR}"
    font-family="monospace"
    font-size="{FONT_SIZE}px"
    opacity="0">{escaped}

    <set
        attributeName="opacity"
        to="1"
        begin="{current_time:.4f}s"
        fill="freeze"
    />

</text>
'''
                )


        # Every column consumes typing time,
        # including spaces.
        current_time += CHAR_DELAY


    # Pause before starting next row
    current_time += ROW_PAUSE


# ============================================================
# CURSOR
#
# This is also generated position-by-position.
#
# A tiny cursor appears at the current character,
# disappears, then appears at the next one.
# ============================================================

if not STATIC:

    cursor_time = 0.0

    for row in range(rows):

        y = row * LINE_HEIGHT

        for col in range(COLS):

            x = col * CHAR_WIDTH

            start = cursor_time

            end = (
                cursor_time
                + CHAR_DELAY
            )

            svg.append(
                f'''
<rect
    x="{x}"
    y="{y + 1}"
    width="{CURSOR_WIDTH}"
    height="{LINE_HEIGHT - 2}"
    fill="{TEXT_COLOR}"
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


        cursor_time += ROW_PAUSE


# ============================================================
# SAVE SVG
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


# ============================================================
# OUTPUT INFORMATION
# ============================================================

print()
print("ASCII portrait generated")
print("------------------------")

print(
    f"Grid: {COLS} x {rows}"
)

print(
    f"Characters: {COLS * rows}"
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
    print("Mode: TRUE CHARACTER TYPEWRITER")

print()