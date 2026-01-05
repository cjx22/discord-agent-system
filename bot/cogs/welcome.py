import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        print(f"[WELCOME] Join detected: {member} in {member.guild}")
        print(f"[WELCOME] system_channel = {member.guild.system_channel}")

        channel = member.guild.system_channel
        if channel is None:
            return

        embed = discord.Embed(
            title="Welcome!",
            description=f"Welcome to the server, {member.mention} 👋",
            color=discord.Color.blue()
        )

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"User ID: {member.id}")

        await channel.send(embed=embed)
