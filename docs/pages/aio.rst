Asyncio Support (AioEditor)
===========================
Demonstration on how to use the AioEditor

.. code-block:: python3

    from easy_pil import AioEditor

    editor = AioEditor(your_image)
    editor.rectangle((0, 0), width=100, height=100, color="black")

    img = await editor.execute() # returns Editor
    # now use `img` in the old way
