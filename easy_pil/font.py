import os

from PIL import ImageFont
from typing_extensions import Literal

fonts_directory = os.path.join(os.path.dirname(__file__), "fonts")
fonts_path = {
    "caveat": {
        "regular": os.path.join(fonts_directory, "caveat", "caveat.ttf"),
        "bold": os.path.join(fonts_directory, "caveat", "caveat.ttf"),
        "italic": os.path.join(fonts_directory, "caveat", "caveat.ttf"),
        "light": os.path.join(fonts_directory, "caveat", "caveat.ttf"),
    },
    "montserrat": {
        "regular": os.path.join(fonts_directory, "montserrat", "montserrat_regular.ttf"),
        "bold": os.path.join(fonts_directory, "montserrat", "montserrat_bold.ttf"),
        "italic": os.path.join(fonts_directory, "montserrat", "montserrat_italic.ttf"),
        "light": os.path.join(fonts_directory, "montserrat", "montserrat_light.ttf"),
    },
    "poppins": {
        "regular": os.path.join(fonts_directory, "poppins", "poppins_regular.ttf"),
        "bold": os.path.join(fonts_directory, "poppins", "poppins_bold.ttf"),
        "italic": os.path.join(fonts_directory, "poppins", "poppins_italic.ttf"),
        "light": os.path.join(fonts_directory, "poppins", "poppins_light.ttf"),
    },
        "arial": {
        "regular": os.path.join(fonts_directory, "arial", "arial.ttf"),
        "bold": os.path.join(fonts_directory, "arial", "arial.ttf"),
        "italic": os.path.join(fonts_directory, "arial", "arial.ttf"),
        "light": os.path.join(fonts_directory, "arial", "arial.ttf"),
    },
        "noto sans": {
        "regular": os.path.join(fonts_directory, "notosans", "NotoSans-Medium.ttf"),
        "bold": os.path.join(fonts_directory, "notosans", "NotoSans-Bold.ttf"),
        "italic": os.path.join(fonts_directory, "notosans", "NotoSans-Italic.ttf"),
        "light": os.path.join(fonts_directory, "notosans", "NotoSans-Light.ttf"),
    },
        "msgothic": {
        "regular": os.path.join(fonts_directory, "msgothic", "msgothic.ttc"),
        "bold": os.path.join(fonts_directory, "msgothic", "msgothic.ttc"),
        "italic": os.path.join(fonts_directory, "msgothic", "msgothic.ttc"),
        "light": os.path.join(fonts_directory, "msgothic", "msgothic.ttc"),
    },
        "PRISTINA": {
        "regular": os.path.join(fonts_directory, "PRISTINA", "PRISTINA.ttf"),
        "bold": os.path.join(fonts_directory, "PRISTINA", "PRISTINA.ttf"),
        "italic": os.path.join(fonts_directory, "PRISTINA", "PRISTINA.ttf"),
        "light": os.path.join(fonts_directory, "PRISTINA", "PRISTINA.ttf"),
    },
        "OLDENGL": {
        "regular": os.path.join(fonts_directory, "OLDENGL", "OLDENGL.ttf"),
        "bold": os.path.join(fonts_directory, "OLDENGL", "OLDENGL.ttf"),
        "italic": os.path.join(fonts_directory, "OLDENGL", "OLDENGL.ttf"),
        "light": os.path.join(fonts_directory, "OLDENGL", "OLDENGL.ttf"),
    },
        "Redressed": {
        "regular": os.path.join(fonts_directory, "Redressed", "Redressed.ttf"),
        "bold": os.path.join(fonts_directory, "Redressed", "Redressed.ttf"),
        "italic": os.path.join(fonts_directory, "Redressed", "Redressed.ttf"),
        "light": os.path.join(fonts_directory, "Redressed", "Redressed.ttf"),
    },
        "NotoSansJP": {
        "regular": os.path.join(fonts_directory, "NotoSansJP", "NotoSansJP.otf"),
        "bold": os.path.join(fonts_directory, "NotoSansJP", "NotoSansJP.otf"),
        "italic": os.path.join(fonts_directory, "NotoSansJP", "NotoSansJP.otf"),
        "light": os.path.join(fonts_directory, "NotoSansJP", "NotoSansJP.otf"),
    },
        "NotoSerif": {
        "regular": os.path.join(fonts_directory, "NotoSerif", "NotoSerif.ttf"),
        "bold": os.path.join(fonts_directory, "NotoSerif", "NotoSerif.ttf"),
        "italic": os.path.join(fonts_directory, "NotoSerif", "NotoSerif.ttf"),
        "light": os.path.join(fonts_directory, "NotoSerif", "NotoSerif.ttf"),
    },
        "Roboto": {
        "regular": os.path.join(fonts_directory, "Roboto", "Roboto.ttf"),
        "bold": os.path.join(fonts_directory, "Roboto", "Roboto.ttf"),
        "italic": os.path.join(fonts_directory, "Roboto", "Roboto.ttf"),
        "light": os.path.join(fonts_directory, "Roboto", "Roboto.ttf"),
    },
        "NotoSerifJP": {
        "regular": os.path.join(fonts_directory, "NotoSerifJP", "NotoSerifJP.otf"),
        "bold": os.path.join(fonts_directory, "NotoSerifJP", "NotoSerifJP.otf"),
        "italic": os.path.join(fonts_directory, "NotoSerifJP", "NotoSerifJP.otf"),
        "light": os.path.join(fonts_directory, "NotoSerifJP", "NotoSerifJP.otf"),
    },
        "JuergenManuscript": {
        "regular": os.path.join(fonts_directory, "JuergenManuscript", "JuergenManuscript.ttf"),
        "bold": os.path.join(fonts_directory, "JuergenManuscript", "JuergenManuscript.ttf"),
        "italic": os.path.join(fonts_directory, "JuergenManuscript", "JuergenManuscript.ttf"),
        "light": os.path.join(fonts_directory, "JuergenManuscript", "JuergenManuscript.ttf"),
    },
        "JuergenStylo": {
        "regular": os.path.join(fonts_directory, "JuergenStylo", "JuergenStylo.ttf"),
        "bold": os.path.join(fonts_directory, "JuergenStylo", "JuergenStylo.ttf"),
        "italic": os.path.join(fonts_directory, "JuergenStylo", "JuergenStylo.ttf"),
        "light": os.path.join(fonts_directory, "JuergenStylo", "JuergenStylo.ttf"),
    },
}

class Font:
    """Font class

    Parameters
    ----------
    path : str
        Path of font
    size : int, optional
        Size of font, by default 10
    """

    def __init__(self, path: str, size: int = 10, **kwargs) -> None:
        self.font = ImageFont.truetype(path, size=size, **kwargs)

    @staticmethod
    def poppins(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """Poppins font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["poppins"][variant], size=size)

    @staticmethod
    def caveat(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """Caveat font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["caveat"][variant], size=size)

    @staticmethod
    def montserrat(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """Montserrat font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["montserrat"][variant], size=size)

    @staticmethod
    def arial(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """Arial font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["arial"][variant], size=size)

    @staticmethod
    def notosans(
       variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """Noto Sans font
        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["noto sans"][variant], size=size)

    @staticmethod
    def msgothic(
       variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """msgothic font
        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["msgothic"][variant], size=size)

    @staticmethod
    def PRISTINA(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """PRISTINA font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["PRISTINA"][variant], size=size)

    @staticmethod
    def OLDENGL(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """OLDENGL font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["OLDENGL"][variant], size=size)

    @staticmethod
    def Redressed(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """Redressed font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["Redressed"][variant], size=size)

    @staticmethod
    def NotoSansJP(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """NotoSansJP font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["NotoSansJP"][variant], size=size)

    @staticmethod
    def NotoSerif(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """NotoSerif font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["NotoSerif"][variant], size=size)

    @staticmethod
    def Roboto(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """Roboto font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["Roboto"][variant], size=size)

    @staticmethod
    def NotoSerifJP(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """NotoSerifJP font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["NotoSerifJP"][variant], size=size)

    @staticmethod
    def JuergenManuscript(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """JuergenManuscript font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["JuergenManuscript"][variant], size=size)

    @staticmethod
    def JuergenStylo(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ):
        """JuergenStylo font

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10
        """
        return ImageFont.truetype(fonts_path["JuergenStylo"][variant], size=size)