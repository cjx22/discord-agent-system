import json
from pathlib import Path
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import discord
from discord.ext import commands

DATA_DIR = Path("data")
CONFIG_FILE = DATA_DIR / "guild_config.json"
ASSETS_DIR = Path("assets")
WELCOME_BG = ASSETS_DIR / "welcome_bg.gif"

async def make_welcome_card(member) -> BytesIO:
    # Load background
    base = Image.open(WELCOME_BG).convert("RGBA")

    # Fetch avatar bytes from Discord
    avatar_bytes = await member.display_avatar.read()
    avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA")

    # Resize avatar
    avatar_size = 160
    avatar = avatar.resize((avatar_size, avatar_size))

    # Make avatar circular mask
    mask = Image.new("L", (avatar_size, avatar_size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)

    # Paste avatar onto background (position as you like)
    x, y = 60, 60
    base.paste(avatar, (x, y), mask)

    # Draw text
    draw = ImageDraw.Draw(base)

    # Font: use a TTF if you have one; otherwise it will default
    # Recommended: include a font file like assets/Inter-Bold.ttf
    font_path = ASSETS_DIR / "Inter-Bold.ttf"
    font_big = ImageFont.truetype(str(font_path), 40) if font_path.exists() else ImageFont.load_default()
    font_small = ImageFont.truetype(str(font_path), 22) if font_path.exists() else ImageFont.load_default()

    welcome_text = f"Welcome, {member.name}!"
    member_count_text = f"Member #{member.guild.member_count}"

    draw.text((240, 80), welcome_text, font=font_big)
    draw.text((240, 135), member_count_text, font=font_small)

    # Export to BytesIO
    out = BytesIO()
    base.save(out, format="PNG")
    out.seek(0)
    return out


def _load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_config(cfg: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cfg = _load_config()

    # ---------- helpers ----------
    def _guild_entry(self, guild_id: int) -> dict:
        gid = str(guild_id)
        if gid not in self.cfg:
            self.cfg[gid] = {
                "welcome_channel_id": None,
                "bye_channel_id": None,
                "welcome_message": "Welcome to the server, {mention} 👋",
                "bye_message": "{name} has left the server. 👋",
            }
            _save_config(self.cfg)
        return self.cfg[gid]

    def _get_text_channel(self, guild: discord.Guild, channel_id: int | None) -> discord.TextChannel | None:
        if not channel_id:
            return None
        ch = guild.get_channel(channel_id)
        return ch if isinstance(ch, discord.TextChannel) else None

    # ---------- commands ----------
    @commands.command(name="setwelcome")
    @commands.has_permissions(manage_guild=True)
    async def setwelcome(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the welcome channel. Example: !setwelcome #welcome"""
        entry = self._guild_entry(ctx.guild.id)
        entry["welcome_channel_id"] = channel.id
        _save_config(self.cfg)
        await ctx.send(f"the welcome channel is set to {channel.mention}")

    @commands.command(name="setbye")
    @commands.has_permissions(manage_guild=True)
    async def setbye(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the leave/bye channel. Example: !setbye #goodbye"""
        entry = self._guild_entry(ctx.guild.id)
        entry["bye_channel_id"] = channel.id
        _save_config(self.cfg)
        await ctx.send(f"the bye channel is set to {channel.mention}")

    @commands.command(name="setwelcomemsg")
    @commands.has_permissions(manage_guild=True)
    async def setwelcomemsg(self, ctx: commands.Context, *, message: str):
        """
        Set the welcome message template.
        Variables: {mention}, {name}, {guild}
        Example: !setwelcomemsg Welcome {mention} to {guild}!
        """
        entry = self._guild_entry(ctx.guild.id)
        entry["welcome_message"] = message
        _save_config(self.cfg)
        await ctx.send("welcome message updated.")

    @commands.command(name="setbyemsg")
    @commands.has_permissions(manage_guild=True)
    async def setbyemsg(self, ctx: commands.Context, *, message: str):
        """
        Set the bye message template.
        Variables: {mention}, {name}, {guild}
        Example: !setbyemsg Rip {name} 💀
        """
        entry = self._guild_entry(ctx.guild.id)
        entry["bye_message"] = message
        _save_config(self.cfg)
        await ctx.send("bye message updated.")

    @commands.command(name="clearwelcome")
    @commands.has_permissions(manage_guild=True)
    async def clearwelcome(self, ctx: commands.Context):
        """Clear the welcome channel (falls back to system channel)."""
        entry = self._guild_entry(ctx.guild.id)
        entry["welcome_channel_id"] = None
        _save_config(self.cfg)
        await ctx.send("the welcome channel was cleared. it will fall back to the system channel (if set).")

    @commands.command(name="clearbye")
    @commands.has_permissions(manage_guild=True)
    async def clearbye(self, ctx: commands.Context):
        """Clear the bye channel (falls back to system channel)."""
        entry = self._guild_entry(ctx.guild.id)
        entry["bye_channel_id"] = None
        _save_config(self.cfg)
        await ctx.send("the bye channel was cleared. it will fall back to the system channel (if set).")

    # ---------- events ----------
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        entry = self._guild_entry(member.guild.id)

        # pick channel first
        channel = (
            self._get_text_channel(member.guild, entry["welcome_channel_id"])
            or member.guild.system_channel
        )
        if channel is None:
            return

        # 1) Send the welcome card image
        card = await make_welcome_card(member)
        file = discord.File(card, filename="welcome.png")
        await channel.send(content=member.mention, file=file)

        # 2) Send the embed message (optional)
        msg = entry["welcome_message"].format(
            mention=member.mention,
            name=member.name,
            guild=member.guild.name,
        )
        embed = discord.Embed(title="Welcome!", description=msg)
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        entry = self._guild_entry(member.guild.id)

        # prefer configured bye channel; fallback to system channel
        channel = self._get_text_channel(member.guild, entry["bye_channel_id"]) or member.guild.system_channel
        if channel is None:
            return

        msg = entry["bye_message"].format(
            mention=member.mention,
            name=member.name,
            guild=member.guild.name,
        )

        embed = discord.Embed(title="Goodbye!", description=msg)
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)
