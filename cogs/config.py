"""
This file contains the cog for managing bot's configuration. It will likely be restructured in the future.
"""

from typing import TYPE_CHECKING

import discord
from discord import app_commands, ui
from discord.ext import commands

from config import config, strings as _strings
from utils.context import WhiteContext

if TYPE_CHECKING:
    from ..bot import Bot


strings = _strings.config.beta_features_menu


class ManageConfigSelect(ui.Select):
    def __init__(self, context: "WhiteContext"):
        assert context.settings is not None
        self.settings = context.settings
        super().__init__(
            options=[
                discord.SelectOption(
                    label=feature["name"], 
                    value=feature["flag_name"],
                    default=getattr(self.settings.flags, feature["flag_name"])
                ) 
                for feature in strings.availible_features
            ],
            min_values=0,
            max_values=len(strings.availible_features)
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        for feature in strings.availible_features:
            if feature["flag_name"] in self.values:
                setattr(self.settings.flags, feature["flag_name"], True)
            else:
                setattr(self.settings.flags, feature["flag_name"], False)

        await self.settings.update(flags=self.settings.flags)

        await interaction.edit_original_message(
            content=f"{config.emojis.success} {strings.feature_list_updated}",
            view=None
        )


class ChangeConfigView(ui.View):
    def __init__(self, *, context: "WhiteContext"):
        super().__init__()
        self.context = context

    @ui.button(label=strings.manage_features)
    async def manage_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user != self.context.author:
            await interaction.response.send_message(
                f"{config.emojis.error} {strings.access_denied}",
                ephemeral=True
            )
            return
        
        select_view = ui.View()
        select_view.add_item(ManageConfigSelect(self.context))
        await interaction.response.send_message(
            strings.choose_features,
            view=select_view,
            ephemeral=True
        )


class Config(commands.Cog):
    def __init__(self, bot: "Bot"):
        self.bot = bot

    @commands.hybrid_group()
    @commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def config(self, _):
        pass

    @config.command()
    async def beta(self, ctx: "WhiteContext"):
        """
        Открывает настройки бета-функций бота
        """
        if ctx.interaction is None:
            return

        assert ctx.settings is not None
        await ctx.settings.query("flags")
        assert ctx.settings.flags is not None

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
            view=ChangeConfigView(context=ctx)
        )


async def setup(bot: "Bot"):
    await bot.add_cog(Config(bot))

async def teardown(bot: "Bot"):
    await bot.remove_cog("config")