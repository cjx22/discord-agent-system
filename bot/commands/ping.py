from discord.ext import commands

@commands.command()
async def ping(ctx):
    """Simple health check command."""
    await ctx.send("pong")