import re

import aiohttp
from bs4 import BeautifulSoup

import slash
from .wiki import Wiki
from .errors import WikiNotFound

class WikiConverter(slash.AutocompleteConverter):
    async def get_suggestions(self, ctx, argument):
        if argument == "":
            await ctx.settings.query_wiki_info()
            return [
                slash.Choice(name=ctx.settings.bound_wiki_name, value=ctx.settings.bound_wiki_url)
            ]
        
        async with ctx.bot.session.get(
            "https://community.fandom.com/wiki/Special:NewWikis",
            params=dict(start=argument, limit=5)
        ) as resp:
            text = await resp.text()

        soup = BeautifulSoup(text, "html.parser")
        return [
            slash.Choice(name=element.text, value=element.get("href"))
            for element in soup.select(".mw-spcontent ul li a")
        ]

    async def convert(self, ctx, argument):
        if re.match(r"https?:\/\/", argument):
            return Wiki(url=argument, session=ctx.bot.session)

        return Wiki.from_dot_notation(argument, session=ctx.bot.session)

class PageConverter(slash.AutocompleteConverter):
    async def get_suggestions(self, ctx, argument):
        if ctx.kwargs.get("wiki"):
            wiki = await WikiConverter().convert(ctx, ctx.kwargs["wiki"])
        else:
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
            slash.Choice(name=suggestion, value=suggestion)
            for suggestion in search["suggestions"]
        ]

    async def convert(self, ctx, argument):
        return argument