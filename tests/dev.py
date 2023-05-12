from easy_pil import Editor, Workspace

space = Workspace((200, 200))
space.create_layer("background", "black")
space.update_layer("background", new_layer_name="good")
space.set_working_layer("good")

space.add_component(
    identifier="cube",
    func=Editor.rectangle,
    options={
        "position": (0, 0),
        "color": "red",
        "width": 100,
        "height": 100,
    },
)

img = space.generate_image()
img.show()
