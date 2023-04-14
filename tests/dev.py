from easy_pil import Editor, Workspace

space = Workspace((200, 200))
space.create_layer("background", "black")
space.set_working_layer("background")

space.add_component(
    identifier="cube",
    func=Editor.rectangle,
    position=(0, 0),
    color="red",
    width=100,
    height=100,
)

space.generate_image().show()
space.remove_layer("background")

space.generate_image().show()
