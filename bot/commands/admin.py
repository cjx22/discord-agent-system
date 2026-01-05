from discord.ext import commands

@commands.command()
@commands.has_permissions(manage_guild=True)
async def say(ctx, *, message: str):
    """Admin-only: make the bot repeat a message."""
    await ctx.send(message)

@commands.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    """
    Admin-only: delete the last N messages in the current channel.
    Example: !purge 10
    """
    # Safety guardrails
    if amount <= 0:
        await ctx.send("Amount must be a positive number. Example: `!purge 10`")
        return

    # Hard cap so nobody nukes a channel by accident
    amount = min(amount, 100)

    # +1 to also remove the command message itself
    deleted = await ctx.channel.purge(limit=amount + 1)

    # deleted includes the command message, so subtract 1 for the user's request
    deleted_count = max(0, len(deleted) - 1)

    # Auto-delete the confirmation after a few seconds to keep chat clean
    await ctx.send(f"🧹 Deleted {deleted_count} message(s).", delete_after=5)