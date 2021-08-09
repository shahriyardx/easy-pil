import os
from PIL import ImageFont
from typing import Literal


class Font:
    def __init__(self, path: str = None, size: int = 10, **kwargs) -> None:
        if path:
            self.font = ImageFont.truetype(path, size=size, **kwargs)

        fonts_directory = os.path.join(os.path.dirname(__file__), "fonts")

        self.__fonts_path = {
            "caveat": {
                "regular": os.path.join(fonts_directory, "caveat", "caveat.ttf"),
                "bold": os.path.join(fonts_directory, "caveat", "caveat.ttf"),
                "italic": os.path.join(fonts_directory, "caveat", "caveat.ttf"),
                "light": os.path.join(fonts_directory, "caveat", "caveat.ttf"),
            },
            "montserrat": {
                "regular": os.path.join(
                    fonts_directory, "montserrat", "montserrat_regular.ttf"
                ),
                "bold": os.path.join(
                    fonts_directory, "montserrat", "montserrat_bold.ttf"
                ),
                "italic": os.path.join(
                    fonts_directory, "montserrat", "montserrat_italic.ttf"
                ),
                "light": os.path.join(
                    fonts_directory, "montserrat", "montserrat_light.ttf"
                ),
            },
            "poppins": {
                "regular": os.path.join(
                    fonts_directory, "poppins", "poppins_regular.ttf"
                ),
                "bold": os.path.join(fonts_directory, "poppins", "poppins_bold.ttf"),
                "italic": os.path.join(
                    fonts_directory, "poppins", "poppins_italic.ttf"
                ),
                "light": os.path.join(fonts_directory, "poppins", "poppins_light.ttf"),
            },
        }

    def poppins(
        self,
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size=10,
    ):
        return ImageFont.truetype(self.__fonts_path["poppins"][variant], size=size)

    def caveat(
        self,
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size=10,
    ):
        return ImageFont.truetype(self.__fonts_path["caveat"][variant], size=size)

    def montserrat(
        self,
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size=10,
    ):
        return ImageFont.truetype(self.__fonts_path["montserrat"][variant], size=size)
