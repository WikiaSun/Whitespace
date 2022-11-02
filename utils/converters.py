import re
from typing import TYPE_CHECKING

import aiohttp
from bs4 import BeautifulSoup
from discord import app_commands
import discord

from utils.context import WhiteContext
from .wiki import Wiki
from .errors import WikiNotFound
if TYPE_CHECKING:
    from bot import Bot

class WikiConverter(app_commands.Transformer):
    @classmethod
    async def autocomplete(cls, interaction: discord.Interaction, value: str):
        ctx = await WhiteContext.from_interaction(interaction)
        if value == "":
            if ctx.settings is None:
                return []

            await ctx.settings.query_wiki_info()
            return [
                app_commands.Choice(name=ctx.settings.bound_wiki_name, value=ctx.settings.bound_wiki_url) # type: ignore  # information queried
            ]
        
        async with ctx.bot.session.get(
            "https://community.fandom.com/wiki/Special:NewWikis",
            params=dict(start=value, limit=5)
        ) as resp:
            text = await resp.text()

        soup = BeautifulSoup(text, "html.parser")
        return [
            app_commands.Choice(name=element.text, value=element.get("href"))
            for element in soup.select(".mw-spcontent ul li a")
        ]

    @classmethod
    def common_convert(cls, bot: "Bot", argument: str) -> Wiki:
        if re.match(r"https?:\/\/", argument):
            return Wiki(url=argument, session=bot.session)

        return Wiki.from_dot_notation(argument, session=bot.session)

    @classmethod
    async def convert(cls, ctx: WhiteContext, argument: str) -> Wiki:
        return cls.common_convert(ctx.bot, argument)

    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str) -> Wiki:
        return cls.common_convert(interaction.client, value)


class PageConverter(app_commands.Transformer):
    @classmethod
    async def autocomplete(cls, interaction: discord.Interaction, argument: str):
        ctx = await WhiteContext.from_interaction(interaction)
        
        if interaction.namespace.wiki:
            wiki = await WikiConverter().convert(ctx, interaction.namespace.wiki)
        else:
            if ctx.settings is None:
                return []
                
            await ctx.settings.query_wiki_info()
            wiki = ctx.wiki
        
        try:
            search = await wiki.query_nirvana(
                controller="UnifiedSearchSuggestionsController",
                method="getSuggestions",
                query=argument
            )
        except (aiohttp.ContentTypeError, aiohttp.ClientConnectorError) as exc:
            return []

        return [
            app_commands.Choice(name=suggestion, value=suggestion)
            for suggestion in search["suggestions"]
        ]

    @classmethod
    async def convert(cls, ctx, argument):
        return argument

    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str) -> str:
        return value


class AccountConverter(app_commands.Transformer):
    pass