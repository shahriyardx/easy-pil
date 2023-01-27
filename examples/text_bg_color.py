from easy_pil import Canvas, Editor, Font

bg = Editor(Canvas(width=300, height=200, color="white"))
font_1 = Font.poppins(variant="regular", size=30)
font_2 = Font.poppins(variant="regular", size=50)

text_1 = "hello"
text_2 = "Your Name"

text_1_x, text_1_y = font_1.getsize(text_1)
text_2_x, text_2_y = font_2.getsize(text_2)

bg.rectangle((10, 10), text_1_x + 8, text_1_y + 5, "black")
bg.rectangle((10, 50), text_2_x + 8, text_2_y + 5, "black")

bg.text((15, 18), text_1, font_1, "white")
bg.text((15, 60), text_2, font_2, "red")

bg.show()
