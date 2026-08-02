from PIL import Image
import html

INPUT = "source-prepped.png"
OUTPUT = "avi-ascii.svg"

# Number of ASCII characters horizontally
COLS = 100

# IMPORTANT: bright -> dark
RAMP = " .`:-=+*cs#%@"

FONT_SIZE = 10
CHAR_WIDTH = 6
LINE_HEIGHT = 10

# Light gray ASCII on dark background
TEXT_COLOR = "#b8b8b8"
BACKGROUND = "#0d1117"


def brightness_to_char(value):
    """
    value:
        255 = white
        0   = black

    White -> space
    Black -> @
    """

    normalized = 1 - (value / 255.0)

    index = int(
        normalized * (len(RAMP) - 1)
    )

    return RAMP[index]


# ---------------------------------------
# Load prepped image
# ---------------------------------------

img = Image.open(INPUT).convert("L")

aspect_ratio = img.height / img.width

# Compensate for character dimensions
rows = int(
    COLS * aspect_ratio * 0.52
)

img = img.resize((COLS, rows))

pixels = img.load()


# ---------------------------------------
# Convert pixels -> ASCII
# ---------------------------------------

ascii_rows = []

for y in range(rows):

    line = ""

    for x in range(COLS):

        brightness = pixels[x, y]

        char = brightness_to_char(brightness)

        line += char

    ascii_rows.append(line)


# ---------------------------------------
# SVG dimensions
# ---------------------------------------

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


# ---------------------------------------
# Background
# ---------------------------------------

svg.append(
    f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>'
)


# ---------------------------------------
# Create animated clip paths
# ---------------------------------------

svg.append("<defs>")


for i in range(rows):

    y = i * LINE_HEIGHT

    delay = i * 0.035

    svg.append(
        f'''
        <clipPath id="clip-{i}">

            <rect
                x="0"
                y="{y}"
                width="0"
                height="{LINE_HEIGHT + 2}">

                <animate
                    attributeName="width"
                    from="0"
                    to="{WIDTH}"
                    dur="1.2s"
                    begin="{delay}s"
                    fill="freeze"
                />

            </rect>

        </clipPath>
        '''
    )


svg.append("</defs>")


# ---------------------------------------
# ASCII text
# ---------------------------------------

for i, line in enumerate(ascii_rows):

    y = (i + 1) * LINE_HEIGHT

    escaped = html.escape(line)

    svg.append(
        f'''
        <text
            x="0"
            y="{y}"
            fill="{TEXT_COLOR}"
            font-family="monospace"
            font-size="{FONT_SIZE}px"
            xml:space="preserve"
            clip-path="url(#clip-{i})">{escaped}</text>
        '''
    )


# ---------------------------------------
# Cursor
# ---------------------------------------

for i in range(rows):

    y = i * LINE_HEIGHT

    delay = i * 0.035

    svg.append(
        f'''
        <rect
            x="0"
            y="{y}"
            width="5"
            height="{LINE_HEIGHT}"
            fill="{TEXT_COLOR}"
            opacity="0">

            <animate
                attributeName="opacity"
                values="0;1;1;0"
                dur="1.2s"
                begin="{delay}s"
                fill="freeze"
            />

            <animate
                attributeName="x"
                from="0"
                to="{WIDTH}"
                dur="1.2s"
                begin="{delay}s"
                fill="freeze"
            />

        </rect>
        '''
    )


svg.append("</svg>")


# ---------------------------------------
# Save SVG
# ---------------------------------------

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))


print()
print("ASCII SVG generated successfully!")
print(f"Grid: {COLS} x {rows}")
print(f"Output: {OUTPUT}")
print()