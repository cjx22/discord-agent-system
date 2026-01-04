import discord
from discord.ext import commands
import os

from bot.commands.ping import ping
from bot.commands.echo import echo

from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_command_error(ctx, error):
    # If the command has its own error handler, don't double-handle
    if hasattr(ctx.command, "on_error"):
        return

    # Missing required arguments (e.g., user typed `!echo` with nothing)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: `{error.param.name}`. Try: `!{ctx.command} <text>`")
        return

    # Unknown command (optional—comment out if you don't want this)
    if isinstance(error, commands.CommandNotFound):
        return  # silently ignore unknown commands

    # Bad argument type (e.g., expecting int but got text)
    if isinstance(error, commands.BadArgument):
        await ctx.send("Bad argument type. Check your input and try again.")
        return

    # Anything else: show a generic message and print the real error to console
    await ctx.send("Something went wrong while running that command.")
    raise error  # so you still see the traceback in your terminal

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.add_command(ping)
bot.add_command(echo)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN not set")

    bot.run(token)
