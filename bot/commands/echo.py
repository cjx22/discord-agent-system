from discord.ext import commands

@commands.command()
async def echo(ctx, *, message: str):
    """Echo back the user's message."""
    await ctx.send(message)