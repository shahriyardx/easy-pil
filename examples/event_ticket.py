"""Concert / event ticket with a detachable perforated stub.

Showcases: a vibrant festival background with soft bokeh lights, a deep-purple
ticket body with a warm gold display title, a dashed perforation seam with two
punched notch cut-outs, and a fully procedural "QR" code (a fixed deterministic
module grid with three finder squares). Self-contained — no external assets.
"""

from pathlib import Path

from easy_pil import DropShadow, Editor, Font
from easy_pil.canvas import Canvas
from easy_pil.gradient import LinearGradient, RadialGradient

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

# ---- Geometry -------------------------------------------------------------
PAD = 50  # breathing room around the ticket for its drop shadow
TW, TH = 1000, 360  # ticket body size
W, H = TW + PAD * 2, TH + PAD * 2  # 1100 x 460
RADIUS = 30

STUB_W = 290
PERF_X = PAD + (TW - STUB_W)  # seam x (760)
STUB_CX = PERF_X + STUB_W // 2  # stub content centre x
TOP = PAD
BOT = PAD + TH

# ---- Palette --------------------------------------------------------------
GOLD = "#ffd166"
INK = "#ffffff"
MUTE = "#c9b8e8"
TICKET = LinearGradient(["#2b0f54", "#5a189a", "#9d4edd"], direction="diagonal")
GOLD_GRAD = LinearGradient(["#ffe6a1", "#ffd166", "#ff9e2c"], direction="diagonal")

# ---- Background: warm festival gradient + dark vignette + bokeh ------------
bg = Editor(
    Canvas(
        (W, H),
        color=LinearGradient(["#ff9a3c", "#ff2d7e", "#8e2de2"], direction="diagonal"),
    )
)
vignette = Editor(
    Canvas(
        (W, H),
        color=RadialGradient(
            ["#00000000", "#00000000", "#1a0033cc"], center=(0.5, 0.45)
        ),
    )
)
bg.paste(vignette, (0, 0))

bokeh = Editor(Canvas((W, H), color=(0, 0, 0, 0)))
for bx, by, br in [
    (120, 90, 46),
    (250, 380, 30),
    (940, 70, 38),
    (1030, 320, 52),
    (700, 40, 22),
    (60, 300, 26),
]:
    bokeh.ellipse((bx - br, by - br), br * 2, br * 2, fill=(255, 255, 255, 40))
bg.paste(bokeh.blur("gaussian", 9), (0, 0), opacity=0.9)


# ---- QR code: procedural fixed pattern ------------------------------------
def draw_qr(ed: Editor, ox: int, oy: int, modules: int, cell: int) -> None:
    """Draw a fake-but-convincing QR: finder squares + deterministic data."""
    dark = "#241245"

    def in_finder(r: int, c: int) -> bool:
        return (
            (r < 8 and c < 8)
            or (r < 8 and c >= modules - 8)
            or (r >= modules - 8 and c < 8)
        )

    def finder(fr: int, fc: int) -> None:
        px, py = ox + fc * cell, oy + fr * cell
        ed.rectangle((px, py), cell * 7, cell * 7, fill=dark, radius=cell)
        ed.rectangle(
            (px + cell, py + cell), cell * 5, cell * 5, fill="#ffffff", radius=cell
        )
        ed.rectangle(
            (px + cell * 2, py + cell * 2),
            cell * 3,
            cell * 3,
            fill=dark,
            radius=cell // 2,
        )

    for r in range(modules):
        for c in range(modules):
            if in_finder(r, c):
                continue
            if ((r * c + r * 5 + c * 3) % 7) in (0, 2, 3):
                ed.rectangle((ox + c * cell, oy + r * cell), cell, cell, fill=dark)

    finder(0, 0)
    finder(0, modules - 7)
    finder(modules - 7, 0)


# ---- Build the ticket on a padded transparent canvas ----------------------
ticket = Editor(Canvas((W, H), color=(0, 0, 0, 0)))
ticket.rectangle((PAD, PAD), TW, TH, fill=TICKET, radius=RADIUS)

# Subtle top sheen: a white-to-transparent vertical fade (no hard edge).
sheen = Editor(Canvas((TW, 150), color=(0, 0, 0, 0)))
sheen.rectangle(
    (0, 0),
    TW,
    150,
    radius=RADIUS,
    fill=LinearGradient(["#ffffff30", "#ffffff00"], direction="vertical"),
)
ticket.paste(sheen, (PAD, PAD))

# ---- Main section ---------------------------------------------------------
MX = PAD + 46
main_right = PERF_X - 46

ticket.text(
    (MX, TOP + 40),
    "L I V E   I N   C O N C E R T",
    font=Font.poppins(variant="bold", size=17),
    color=GOLD,
)

title = "NEON HORIZON"
title_font = ticket.fit_text(
    title,
    main_right - MX,
    Font.poppins(variant="bold", size=80),
    max_size=80,
    min_size=40,
)
ticket.gradient_text((MX, TOP + 70), title, title_font, GOLD_GRAD)

ticket.text(
    (MX, TOP + 158),
    "The Midnight Skyline Tour",
    font=Font.poppins(variant="italic", size=27),
    color=MUTE,
)

# Divider above the info row.
DIV_Y = TOP + 220
ticket.line((MX, DIV_Y), (main_right, DIV_Y), width=2, fill=(255, 255, 255, 55))

# Info trio: small gold label + bold white value.
info = [
    (MX, "DATE", "SAT · AUG 15"),
    (MX + 250, "VENUE", "Sunset Arena"),
    (MX + 500, "DOORS", "8:00 PM"),
]
for ix, label, value in info:
    ticket.text(
        (ix, DIV_Y + 24), label, font=Font.poppins(variant="bold", size=15), color=GOLD
    )
    ticket.text(
        (ix, DIV_Y + 46), value, font=Font.poppins(variant="bold", size=27), color=INK
    )

# ---- Perforation seam: dashed line -----------------------------------------
NOTCH_R = 24
y = TOP + NOTCH_R + 8
while y < BOT - NOTCH_R - 4:
    ticket.rectangle((PERF_X - 2, y), 4, 13, fill=(255, 255, 255, 235), radius=2)
    y += 22

# ---- Stub section ---------------------------------------------------------
ticket.text(
    (STUB_CX, TOP + 42),
    "A D M I T   O N E",
    font=Font.poppins(variant="bold", size=16),
    color=GOLD,
    anchor="mm",
)

stats = [(-88, "SEC", "A2"), (0, "ROW", "07"), (88, "SEAT", "14")]
for dx, label, value in stats:
    ticket.text(
        (STUB_CX + dx, TOP + 78),
        label,
        font=Font.poppins(variant="bold", size=13),
        color=MUTE,
        anchor="mm",
    )
    ticket.text(
        (STUB_CX + dx, TOP + 100),
        value,
        font=Font.poppins(variant="bold", size=26),
        color=INK,
        anchor="mm",
    )

# QR white panel + procedural code.
QN, QCELL = 21, 6
QR_SIZE = QN * QCELL  # 126
PANEL = QR_SIZE + 26  # 152
panel_x = STUB_CX - PANEL // 2
panel_y = TOP + 132
ticket.rectangle((panel_x, panel_y), PANEL, PANEL, fill="#ffffff", radius=16)
draw_qr(ticket, panel_x + 13, panel_y + 13, QN, QCELL)

ticket.text(
    (STUB_CX, panel_y + PANEL + 20),
    "No. 0042 · 8815-A2",
    font=Font.poppins(variant="bold", size=15),
    color=GOLD,
    anchor="mm",
)

# ---- Punch the two notch cut-outs (transparent holes on the seam) ---------
for cy in (TOP, BOT):
    ticket.ellipse(
        (PERF_X - NOTCH_R, cy - NOTCH_R), NOTCH_R * 2, NOTCH_R * 2, fill=(0, 0, 0, 0)
    )

# ---- Shadow + compose -----------------------------------------------------
ticket.effect(DropShadow(offset=(0, 22), blur_radius=38, color=(20, 0, 40), alpha=0.5))
bg.paste(ticket, (0, 0))

bg.save(OUT / "event_ticket.png")
print("saved", OUT / "event_ticket.png", bg.image.size)
