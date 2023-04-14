import random
import string
from typing import Any, Callable, Dict, Tuple, Union

from .types import Color, ComponentKwargs
from .editor import Canvas, Editor


class Workspace:
    """Workspace class for working with layers and components"""

    def __init__(self, size: Tuple[float, float]) -> None:
        self.size = size
        self.layers: Dict[str, Dict[str, Dict[str, dict]]] = dict()
        self.working_layer = None

    def create_layer(self, name: str, background: Color = (0, 0, 0, 0)):
        """Creates a layer

        Parameters
        ----------
        name : str
            name of the layer
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
        **kwargs: ComponentKwargs
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
        kwargs : dict
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
            **kwargs,
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
        self, *, layer_name: str = None, identifier: str, **kwargs: ComponentKwargs
    ):
        """Update component of a layer

        Parameters
        ----------
        layer_name : str
            name of the layer
        identifier : str
            unique name for a component
        kwargs : dict
            modified kwargs

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

        self.layers[layer_name]["components"][identifier].update(kwargs)

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

            for _, kwargs in layer["components"].items():
                _kwargs = {**kwargs}

                _func = getattr(_layer, _kwargs.pop("func_name"))

                if _func:
                    _func(**_kwargs)

            editor.paste(_layer, position=(0, 0))

        return editor
