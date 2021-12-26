from __future__ import annotations
import re
from typing import TYPE_CHECKING, Dict, List, Optional

from discord.ext import commands
import discord

if TYPE_CHECKING:
    from bot import Bot
    from utils.wiki import Wiki
    from utils.context import WhiteContextBase

WIKILINK_REGEX = re.compile(r"\[\[(.+?)(?:\|(.*?))?\]\]")
CODEBLOCK_REGEX = re.compile(r"(`{1,3}).*?\1", re.DOTALL)

class Link:
    def __init__(self, match: re.Match, wiki: Wiki) -> None:
        self.target: str = match.group(1)
        self.title: Optional[str] = match.group(2)

        if self.title == "":
            self.title = self.target.split(":")[-1]
        if self.title is None:
            self.title = self.target

        self.url = wiki.url_to(self.target)
        self.match = match
    
    def __repr__(self):
        return f"<Link target={self.target} title={self.title} url={self.url}>"

    def to_hyperlink(self) -> str:
        return f"[{self.title}]({self.url})"

    def to_link(self) -> str:
        return f"<{self.url}>"

class Wikilinks(commands.Cog):
    """Преобразовывает [[текст в квадратных скобках]] в ссылки на статьи на вики."""

    def __init__(self, bot: Bot):
        self.bot = bot

    def _parse_wikilinks(self, ctx: WhiteContextBase, text: str) -> Dict[str, Link]:
        codeblock_matches = list(CODEBLOCK_REGEX.finditer(text))

        links = {}
        for link in WIKILINK_REGEX.finditer(text):
            is_within_codeblock = False
            
            for match in codeblock_matches:
                if link.start(0) > match.start(0) and link.end(0) < match.end(0):
                    is_within_codeblock = True

            if is_within_codeblock:
                continue
            
            links[link.group(1)] = Link(link, wiki=ctx.wiki)

        return links

    async def find_wikilinks(self, ctx: WhiteContextBase, text: str) -> List[Link]:
        links = self._parse_wikilinks(ctx, text)
        if len(links) == 0:
            return []

        interwiki = await ctx.wiki.query(
            titles="".join(links),
            iwurl=True
        )
        for entry in interwiki["query"].get("interwiki", []):
            links[entry["title"]].url = entry["url"]

        return list(links.values())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        
        ctx = await self.bot.get_context(message)
        await ctx.settings.query_wiki_info() # type: ignore # type checker cannot figure out that when ctx.guild is not None, ctx.settings is also not None
        links = await self.find_wikilinks(ctx, message.content)


def setup(bot: Bot) -> None:
    bot.add_cog(Wikilinks(bot))
