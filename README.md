# Easy PIL

[![PyPI](https://img.shields.io/pypi/v/easy-pil)](https://pypi.org/project/easy-pil/)
[![Lint & Test](https://github.com/shahriyardx/easy-pil/actions/workflows/lint-test.yml/badge.svg)](https://github.com/shahriyardx/easy-pil/actions/workflows/lint-test.yml)
[![License](https://img.shields.io/github/license/shahriyardx/easy-pil)](https://github.com/shahriyardx/easy-pil/blob/master/LICENSE)

A Python library built on top of [Pillow](https://github.com/python-pillow/Pillow) to easily edit/modify images.

## Installation

```bash
pip install easy-pil
```

Requires Python 3.11 or higher.

## Quick Example

```python
from easy_pil import Editor, Canvas

canvas = Canvas(width=500, height=500)
editor = Editor(canvas)

editor.text((10, 10), "Hello World")
editor.show()  # or .save("output.png")
```

## Documentation

- [Introduction](https://easy-pil.readthedocs.io/en/latest/pages/intro.html)
- [Discord Bot Integration](https://easy-pil.readthedocs.io/en/latest/pages/discordbot.html)
- [Examples](https://github.com/shahriyardx/easy-pil/tree/master/examples)
- [API Reference](https://easy-pil.readthedocs.io/en/latest/easy_pil/modules.html)

## Support

- [Discord Server](https://discord.gg/fVzt5THTNb)
- [YouTube Tutorials](https://www.youtube.com/playlist?list=PLb_oBhGqAlbT4yVqV0TSXggA8b0lZhGhn)
- [Report a Bug](https://github.com/shahriyardx/easy-pil/issues/)
