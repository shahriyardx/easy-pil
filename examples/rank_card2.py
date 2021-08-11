from easy_pil import Canvas, Editor, Font, Text

user_data = {  # Most likely coming from database or calculation
    "name": "Shahriyar#9770",  # The user's name
    "xp": "1.2k",
    "next_level_xp": "5k",
    "level": "5",
    "percentage": 45,
    "rank": 10,
}

background = Editor(canvas=Canvas((934, 282), "#23272a"))
profile = Editor("assets/pfp.png").resize((190, 190)).circle_image()

# For profile to use users profile picture load it from url using the load_image/load_image_async function
# profile_image = load_image(str(ctx.author.avatar_url))
# profile = Editor(profile_image).resize((150, 150)).circle_image()


poppins = Font().poppins(size=30)

background.rectangle((20, 20), 894, 242, "#2a2e35")
background.paste(profile.image, (50, 50))
background.ellipse((42, 42), width=206, height=206, outline="#43b581", stroke_width=10)
background.rectangle((260, 180), width=630, height=40, fill="#484b4e", radius=20)
background.bar(
    (260, 180),
    max_width=630,
    height=40,
    percentage=user_data["percentage"],
    fill="#00fa81",
    radius=20,
)
background.text((270, 120), user_data["name"], font=poppins, color="#00fa81")
background.text(
    (870, 125),
    f"{user_data['xp']} / {user_data['next_level_xp']}",
    font=poppins,
    color="#00fa81",
    align="right",
)

rank_level_texts = [
    Text("Rank ", color="#00fa81", font=poppins),
    Text(f"{user_data['rank']}", color="#1EAAFF", font=poppins),
    Text("   Level ", color="#00fa81", font=poppins),
    Text(f"{user_data['level']}", color="#1EAAFF", font=poppins),
]

background.multicolor_text((850, 30), texts=rank_level_texts, align="right")


background.show()
