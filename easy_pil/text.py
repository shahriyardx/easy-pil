"""Text module for wrapping text and font together."""

from PIL import ImageFont

from .font import Font


class Text:
    """
    Text class.

    Parameters
    ----------
    text : str
        Text
    font : ImageFont.FreeTypeFont
        Font for text
    color : Color, optional
        Font color, by default "black"

    """

    def __init__(
        self,
        text: str,
        font: ImageFont.FreeTypeFont | Font,
        color: int | str | tuple[int, int, int] | tuple[int, int, int, int] = "black",
        anchor: str | None = None,
    ) -> None:
        """Initialize Text with content, font, and color."""
        self.text = text
        self.color = color
        self.anchor = anchor

        if isinstance(font, Font):
            self.font = font.font
        else:
            self.font = font

    def getsize(self) -> tuple[float, float]:
        """
        Get the width and height of the text.

        Returns
        -------
        tuple[float, float]
            Width and height of the text bounding box.

        """
        bbox = self.font.getbbox(self.text)
        return bbox[2], bbox[3]
