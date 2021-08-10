from easy_pil import Canvas, Editor, Font, Text, font


background = Editor(canvas=Canvas((900, 270), "#23272a"))
profile = Editor("assets/pfp.png").resize((200, 200)).circle_image()

square = Canvas((400, 500), "#2C2F33")
square = Editor(canvas=square)
square.rotate(15, expand=True)

poppins_big = Font().poppins(variant="bold", size=50)
poppins_mediam = Font().poppins(variant="bold", size=40)
poppins_regular = Font().poppins(variant="regular", size=30)
poppins_thin = Font().poppins(variant="light", size=18)

# For profile to use users profile picture load it from url using the load_image/load_image_async function
# profile_image = load_image(str(ctx.author.avatar_url))
# profile = Editor(profile_image).resize((150, 150)).circle_image()

background.paste(square.image, (-150,-100))
background.paste(profile.image, (40, 35))
background.ellipse((40, 35), 200, 200, outline="white", stroke_width=3)
background.text((600, 20), "WELCOME", font=poppins_big, color="white", align="center")
background.text((600, 70), "Shahriyar#9770", font=poppins_regular, color="white", align="center")
background.text((600, 120), "YOU ARE MEMBER", font=poppins_mediam, color="white", align="center")
background.text((600, 160), "GUILD 4359", font=poppins_regular, color="white", align="center")
background.text((620, 245), "THANK YOU FOR JOINING. HOPE YOU WILL ENJOY YOUR STAY", font=poppins_thin, color="white", align="center")

background.show()