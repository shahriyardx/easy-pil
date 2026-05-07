from easy_pil import Canvas, Editor, Font, LinearGradient
from pathlib import Path

bg = Editor(Canvas((900, 320), color="#0f0f1a"))

deco_grad = LinearGradient(["#6c5ce7", "#fd79a8"], direction="vertical")
bg.rectangle((0, 0), 350, 320, fill=deco_grad)

profile = (
    Editor(Path(__file__).parent / "assets" / "pfp.png")
    .resize((150, 150))
    .circle_image()
)
bg.paste(profile, (100, 50))
bg.ellipse((100, 50), 150, 150, outline="white", stroke_width=4)

bg.text(
    (175, 230),
    "WELCOME",
    font=Font.poppins(size=36, variant="bold"),
    color="white",
    align="center",
)
bg.text(
    (175, 270),
    "GUILD 4359",
    font=Font.poppins(size=16),
    color="#ddddef",
    align="center",
)

poppins_big = Font.poppins(size=48, variant="bold")
bg.text((550, 70), "Shahriyar#9770", font=poppins_big, color="white")
bg.text(
    (550, 125), "You are the 457th Member", font=Font.poppins(size=22), color="#fd79a8"
)

bg.rectangle((550, 160), 280, 2, fill="#2a2a4a")

details = [
    "Joined: Today at 2:30 PM",
    "Account Age: 2 years",
    "Member #: 000457",
]
for i, line in enumerate(details):
    bg.text((550, 185 + i * 30), line, font=Font.poppins(size=16), color="#8888aa")

grad_btn = LinearGradient(["#6c5ce7", "#fd79a8"], direction="horizontal")
bg.rectangle((550, 270), 180, 40, fill=grad_btn, radius=20)
bg.text(
    (640, 290),
    "GET STARTED",
    font=Font.poppins(size=12, variant="bold"),
    color="white",
    align="center",
)

bg.show()
