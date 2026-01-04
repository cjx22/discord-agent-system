from discord.ext import commands

@commands.command()
@commands.has_permissions(manage_guild=True)
async def say(ctx, *, message: str):
    """Admin-only: make the bot repeat a message."""
    await ctx.send(message)