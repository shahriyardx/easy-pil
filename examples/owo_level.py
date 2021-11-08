from easy_pil import Canvas, Editor, Font


user_data = {
    "name": "Shahriyar#9770",
    "bio": "An Example Bot user",
    "level": "15",
    "xp": "1.2k / 3k",
    "percentage": 45,
}


background = Editor(Canvas((800, 240), color="#23272A"))
profile = Editor("assets/pfp.png").resize((200, 200))

# For profile to use users profile picture load it from url using the load_image/load_image_async function
# profile_image = load_image(str(ctx.author.avatar_url))
# profile = Editor(profile_image).resize((200, 200))


font_40 = Font.poppins(size=40)
font_20 = Font.montserrat(size=20)
font_25 = Font.poppins(size=25)
font_40_bold = Font.poppins(size=40, variant="bold")

background.paste(profile, (20, 20))
background.text((240, 20), user_data["name"], font=font_40, color="white")
background.text((240, 80), user_data["bio"], font=font_20, color="white")
background.text((250, 170), "LVL", font=font_25, color="white")
background.text((310, 155), user_data["level"], font=font_40_bold, color="white")

background.rectangle((390, 170), 360, 25, outline="white", stroke_width=2)
background.bar(
    (394, 174),
    352,
    17,
    percentage=user_data["percentage"],
    fill="white",
    stroke_width=2,
)

background.text((390, 135), "Rank : 45", font=font_25, color="white")
background.text(
    (750, 135), f"XP : {user_data['xp']}", font=font_25, color="white", align="right"
)


background.show()
