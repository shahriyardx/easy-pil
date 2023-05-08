import random
import string
from typing import Any, Callable, Dict, Optional, Tuple, Union

from .editor import Canvas, Editor
from .types.common import Color
from .types.workspace import ComponentKwargs


class Workspace:
    """Workspace class for working with layers and components"""

    def __init__(self, size: Tuple[float, float]) -> None:
        self.size = size
        self.layers: dict = dict()
        self.working_layer = None

    def create_layer(self, name: str, background: Color = (0, 0, 0, 0)):
        """Creates a layer

        Parameters
        ----------
        name : str
            name of the layer
        background: Color
            background color of the layer
        """
        self.layers[name] = {
            "metadata": {
                "background": background,
            },
            "components": dict(),
        }

    def remove_layer(self, name: str):
        """Removes a layer

        Parameters
        ----------
        name : str
            name of the layer

        Raises
        ------
        ValueError
            if the layer is not available in the workspace
        """
        try:
            self.layers.pop(name)
        except KeyError:
            raise ValueError("Invalid layer name")

    def update_layer(
        self,
        layer_name: str,
        new_layer_name: Optional[str] = None,
        background: Optional[Color] = None,
    ):
        """Creates a layer

        Parameters
        ----------
        layer_name : str
            name of the layer
        new_layer_name: str, Optional
            updated name of the layer, defaults to None
        background: Color
            background color of the layer, defaults to None

        Raises
        ------
        ValueError
            if the layer is not available in the workspace
        """
        if layer_name not in self.layers:
            raise ValueError("Invalid layer name")

        if background:
            self.layers[layer_name]["metadata"]["background"] = background

        if new_layer_name:
            self.layers[new_layer_name] = self.layers.pop(layer_name)

    def set_working_layer(self, name: str):
        """Sets a layer as working layer

        Parameters
        ----------
        name : str
            name of the layer

        Raises
        ------
        ValueError
            if the layer is not available in the workspace
        """
        if name not in self.layers:
            raise ValueError("Invalid layer name")

        self.working_layer = name

    def __get_random_identifier(self) -> str:
        return "".join(random.choices(string.ascii_letters, k=5))

    def add_component(
        self,
        *,
        layer_name: str = None,
        identifier: str = None,
        func: Union[Callable, str],
        options: ComponentKwargs
    ):
        """Add component to a layer

        Parameters
        ----------
        layer_name : str
            name of the layer
        identifier : str
            unique name for a component
        func : Union[Callable, str]
            the function or function name from editor class
        options : ComponentKwargs
            keyword arguments for the func

        Raises
        ------
        ValueError
            if the layer is not available in the workspace
        """
        if not self.working_layer and not layer_name:
            raise ValueError(
                "Either specify layer name or set a working layer"
            )

        layer_name = layer_name or self.working_layer

        if layer_name not in self.layers:
            raise ValueError("Invalid layer name")

        func_name = func.__name__ if isinstance(func, Callable) else func
        identifier_name = (
            identifier if identifier else self.__get_random_identifier()
        )

        self.layers[layer_name]["components"][identifier_name] = {
            "func_name": func_name,
            "options": options,
        }

    def remove_component(self, *, layer_name: str = None, identifier: str):
        """Remove component from a layer

        Parameters
        ----------
        layer_name : str
            name of the layer
        identifier : str
            unique name for a component

        Raises
        ------
        ValueError
            if the layer is not available in the workspace
        """

        if not self.working_layer and not layer_name:
            raise ValueError(
                "Either specify layer name or set a working layer"
            )

        layer_name = layer_name or self.working_layer

        try:
            self.layers[layer_name]["components"].pop(identifier)
        except KeyError:
            raise ValueError("Invalid layer name or identifier")

    def update_component(
        self,
        *,
        layer_name: str = None,
        identifier: str,
        options: ComponentKwargs
    ):
        """Update component of a layer

        Parameters
        ----------
        layer_name : str
            name of the layer
        identifier : str
            unique name for a component
        options : ComponentKwargs
            modified options

        Raises
        ------
        ValueError
            if the layer is not available in the workspace
        """
        if not self.working_layer and not layer_name:
            raise ValueError(
                "Either specify layer name or set a working layer"
            )

        layer_name = layer_name or self.working_layer

        if layer_name not in self.layers:
            raise ValueError("Invalid layer name")

        self.layers[layer_name]["components"][identifier]["options"].update(
            options
        )

    def __create_editor_layer(
        self, size: Tuple[float, float], metadata: Dict[str, Any]
    ):
        return Editor(Canvas(size, color=metadata["background"]))

    def generate_image(self) -> Editor:
        """Generates image from the layers

        Returns
        -------
        Editor
            The editor instance
        """
        editor = Editor(Canvas(self.size, color=(0, 0, 0, 0)))

        for layer in self.layers.values():
            _layer = self.__create_editor_layer(self.size, layer["metadata"])

            for config in layer["components"].values():
                func_name = config["func_name"]
                options = config["options"]

                _func = getattr(_layer, func_name)

                if _func:
                    _func(**options)

            editor.paste(_layer, position=(0, 0))

        return editor
