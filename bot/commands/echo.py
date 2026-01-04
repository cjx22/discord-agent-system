from discord.ext import commands

@commands.command()
async def echo(ctx, *, message: str):
    """Echo back the user's message."""
    await ctx.send(message)

@echo.error
async def echo_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!echo <message>`")