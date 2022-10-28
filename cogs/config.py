"""
This file contains the cog for managing bot's configuration. It will likely be restructured in the future.
"""

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from config import config, strings as _strings

if TYPE_CHECKING:
    from ..bot import Bot
    from utils.context import WhiteContext


strings = _strings.config.beta_features_menu

class Config(commands.Cog):
    def __init__(self, bot: "Bot"):
        self.bot = bot

    @commands.hybrid_group()
    @commands.guild_only()
    async def config(self, _):
        pass

    @config.command()
    async def beta(self, ctx: "WhiteContext"):
        """
        Открывает настройки бета-функций бота
        """
        assert ctx.settings is not None
        await ctx.settings.query("flags")

        em = discord.Embed(description=strings.description, color=config.primary_color)
        
        features = []
        for feature in strings.availible_features:
            text = ""
            if getattr(ctx.settings.flags, feature["flag_name"]):
                text += config.emojis.enabled + " "
            else:
                text += config.emojis.disabled + " "
            text += f"**{feature['name']}**\n>>> {feature['description']}"
            
            features.append(text)
        
        em.add_field(
            name=strings.availible_features_title, 
            value="\n\n".join(features)
        )
        await ctx.send(
            f"> {config.emojis.settings} {_strings.config.heading} • **{strings.name}**",
            embed=em,
        )


async def setup(bot: "Bot"):
    await bot.add_cog(Config(bot))

async def teardown(bot: "Bot"):
    await bot.remove_cog("config")