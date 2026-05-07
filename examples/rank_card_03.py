from easy_pil import Canvas, Editor, Font, LinearGradient, Text
from pathlib import Path

user_data = {
    "name": "Shahriyar#9770",
    "xp": "1.2k",
    "next_level_xp": "5k",
    "level": "5",
    "percentage": 45,
    "rank": 10,
}

bg = (
    Editor(Path(__file__).parent / "assets" / "wlcbg.jpg")
    .resize((934, 282))
    .brightness(0.3)
)

profile = (
    Editor(Path(__file__).parent / "assets" / "pfp.png")
    .resize((190, 190))
    .circle_image()
)

poppins = Font.poppins(size=30)
poppins_small = Font.poppins(size=18)

overlay = Editor(Canvas((894, 242), color=(35, 39, 42, 200)))
bg.paste(overlay, (20, 20))
bg.rectangle((20, 20), 894, 242, fill=None, outline="#6c5ce7", stroke_width=2)

bg.paste(profile, (50, 50))
bg.ellipse((42, 42), 206, 206, outline="#43b581", stroke_width=10)

grad = LinearGradient(["#6c5ce7", "#43b581"], direction="horizontal")
bg.rectangle((260, 180), width=630, height=40, fill="#484b4e", radius=20)
bg.bar(
    (260, 180),
    max_width=630,
    height=40,
    percentage=user_data["percentage"],
    fill=grad,
    radius=20,
)

bg.text((270, 50), user_data["name"], font=poppins, color="#6c5ce7")
bg.text(
    (870, 55),
    f"{user_data['xp']} / {user_data['next_level_xp']}",
    font=poppins,
    color="white",
    align="right",
)

desc = Text("Level", color="#8888aa", font=poppins_small)
val = Text(f" {user_data['level']}", color="#43b581", font=poppins)
bg.multi_text((270, 100), texts=[desc, val])

rank_desc = Text("Rank", color="#8888aa", font=poppins_small)
rank_val = Text(f" {user_data['rank']}", color="#fdcb6e", font=poppins)
bg.multi_text((270, 135), texts=[rank_desc, rank_val])

bg.show()
