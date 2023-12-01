from easy_pil import Editor, Workspace, utils, Text, Font
import requests
from io import BytesIO
from PIL import Image

# space = Workspace((200, 200))
# space.create_layer("background", "black")
# space.update_layer("background", new_layer_name="good")
# space.set_working_layer("good")
#
# space.add_component(
#     identifier="cube",
#     func=Editor.rectangle,
#     options={
#         "position": (0, 0),
#         "color": "red",
#         "width": 100,
#         "height": 100,
#     },
# )
#
# img = space.generate_image()
# img.show()

img_path = './tests/assets/animation.gif'
# frames = utils.load_gif(img_path)
# print(frames)
# updated_frames = []
# for f in frames:
#     # f.text((10, 10), "Shahriyar Alam", font=Font.poppins(size=50, variant="bold"))
#     updated_frames.append(Image.open(f))
#
# utils.make_gif(updated_frames, './tests/assets/animation-make.gif')

from PIL import Image, ImageSequence

output_gif_path = './tests/assets/animation-mofdified.gif'

# Open the input GIF file
link = 'https://fiverr-res.cloudinary.com/images/t_main1,q_auto,f_auto,q_auto,f_auto/attachments/delivery/asset/0032398f86ea753194c5eeba97eccda2-1627249600/ExportBackgroundnomoveclound/draw-a-pixel-pokemon-battle-background.gif'

input_gif = utils.load_image(link, raw=True)
print(input_gif)
# Create a list to store modified frames
modified_frames = []

# Iterate over each frame in the GIF
for frame in ImageSequence.Iterator(input_gif):
    print(frame)
    img = Editor(frame)
    img.text((10, 10), text="Shahriyar", font=Font.poppins(size=20))

    modified_frames.append(img.image)

# Save the modified frames as a new GIF
modified_frames[0].save(
    output_gif_path, save_all=True, append_images=modified_frames[1:]
)

# print(f"Modified GIF saved at: {output_gif_path}")
