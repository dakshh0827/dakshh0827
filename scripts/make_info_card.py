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


# --------------------------------------------------
# EDIT YOUR INFORMATION HERE
# --------------------------------------------------

rows = [
    ("Now", "Placement prep + building projects", GREEN),
    ("Prev", "Full-stack development", BLUE),
    ("Stack", "Java · React · Node.js · MongoDB", PURPLE),
    ("Focus", "DSA · Backend · System Design", ORANGE),
    ("Build", "Agentra · MERN · Next.js", GREEN),
    ("Status", "Open to software engineering roles", BLUE),
]


def escape(value):
    return html.escape(value)


svg = []

svg.append(
    f'''<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">
'''
)

# Background
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

# Terminal circles
svg.append('<circle cx="22" cy="22" r="5" fill="#ff5f56"/>')
svg.append('<circle cx="40" cy="22" r="5" fill="#ffbd2e"/>')
svg.append('<circle cx="58" cy="22" r="5" fill="#27c93f"/>')

# Terminal title
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

# Divider
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

# Header
svg.append(
    f'''
    <text
        x="25"
        y="78"
        font-family="{FONT}"
        font-size="15"
        font-weight="bold"
        fill="{GREEN}">
        dakshh0827@github
    </text>
'''
)

svg.append(
    f'''
    <text
        x="25"
        y="100"
        font-family="{FONT}"
        font-size="13"
        fill="{MUTED}">
        ------------------------------
    </text>
'''
)


# Rows
start_y = 135

for i, (key, value, color) in enumerate(rows):

    y = start_y + i * 35

    delay = 0 if STATIC else i * 0.12

    animation = ""

    if not STATIC:
        animation = f'''
            opacity="0"
            transform="translate(0 6)"

            style="
                animation:
                    fade{i} 0.35s ease {delay}s forwards;
            "
        '''

    svg.append(
        f'''
        <text
            x="25"
            y="{y}"
            font-family="{FONT}"
            font-size="13"
            {animation}>
            
            <tspan
                fill="{color}"
                font-weight="bold">
                {escape(key)}
            </tspan>

            <tspan fill="{TEXT}">
                : {escape(value)}
            </tspan>

        </text>
        '''
    )


# Animations

if not STATIC:

    svg.append("<style>")

    for i in range(len(rows)):

        svg.append(
            f'''
            @keyframes fade{i} {{
                from {{
                    opacity: 0;
                    transform: translateY(6px);
                }}

                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            '''
        )

    svg.append("</style>")


svg.append("</svg>")


with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))


print(f"Generated {OUTPUT}")

if STATIC:
    print("Static mode enabled")
else:
    print("Animated mode enabled")
