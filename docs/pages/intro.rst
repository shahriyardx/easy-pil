Introduction
============
This is the documentation for easy-pil, A python library built on top of PIL to easily edit images.

Prerequisties
-------------
easy-pil requires python 3.7 or higher. Support for previous version is not guranteed.

Installing
-----------

Install directly from PyPI: ::

    python3 -m pip install -U easy-pil

If you are using Windows, then the following should be used instead: ::

    py -3 -m pip install -U easy-pil

Basic Concepts
--------------
A quick example of how easy-pil works

.. code-block:: python3

    from easy_pil import Editor, Canvas

    board = Canvas(width=500, height=500)
    editor = Editor(board)

    editor.text((10, 10), "Hello World")
    editor.show() # .save() to save the image
