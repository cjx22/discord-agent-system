@bot.command()
async def ping(ctx):
    """Simple health check command."""
    await ctx.send("pong")