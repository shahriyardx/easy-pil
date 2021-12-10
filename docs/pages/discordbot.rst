Discord bot
=========================
A basic discord bot using `Nextcord <https://nextcord.readthedocs.io>`_ with which uses easy-pil.
This will make command author's avatar circular and send it

.. code-block:: python3

    from nextcord import File
    from nextcord.ext.commands import Bot
    from easy_pil import Editor, load_image_async

    bot = Bot(command_prefix='!')

    @bot.command()
    async def circle(ctx):
        # Load the image using `load_image_async` method
        image = await load_image_async(ctx.author.display_avatar.url)

        # Initialize the editor and pass image as a parameter
        editor = Editor(image).circle_image()

        # Creating nextcord.File object from image_bytes from editor
        file = File(fp=editor.image_bytes, filename='circle.png')
        
        await ctx.send(file=file)
    
    bot.run("TOKEN")