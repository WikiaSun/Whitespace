from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from discord.ext import commands
import discord

from utils.wiki import Wiki
if TYPE_CHECKING:
    from bot import Bot
    from utils.context import WhiteContextBase


def wiki_link(url: str, delimiter: str = "_") -> Callable[[str], str]:
    def get_url(page: str) -> str:
        return url.format(page=page.replace(" ", delimiter))

    return get_url

def internal_wiki_link(link: str) -> str:
    wiki_name, page = link.split(":", 1)
    wiki = Wiki.from_dot_notation(wiki_name)
    return wiki.url_to(page)


WIKILINK_REGEX = re.compile(r"\[\[(.+?)(?:\|(.*?))?\]\]")
CODEBLOCK_REGEX = re.compile(r"(`{1,3}).*?\1", re.DOTALL)
PREFIXES: Dict[str, Callable[[str], str]] = {
    # Fandom
    "w:c":           internal_wiki_link,
    "ww":            wiki_link("https://wikies.fandom.com/wiki/{page}"),
    "w:ru":          wiki_link("https://community.fandom.com/ru/wiki/{page}"),
    "w":             wiki_link("https://community.fandom.com/wiki/{page}"),
    "dev":           wiki_link("https://dev.fandom.com/wiki/{page}"),
    "soap":          wiki_link("https://soap.fandom.com/wiki/{page}"),

    # Wikipedia
    "wp:ru":         wiki_link("https://ru.wikipedia.org/wiki/{page}"),
    "wikipedia:ru":  wiki_link("https://ru.wikipedia.org/wiki/{page}"),
    "wp":            wiki_link("https://en.wikipedia.org/wiki/{page}"),
    "wikipedia":     wiki_link("https://en.wikipedia.org/wiki/{page}"),

    # Wiktionary
    "wiktionary:ru": wiki_link("https://ru.wiktionary.org/wiki/{page}"),
    "wikt:ru":       wiki_link("https://ru.wiktionary.org/wiki/{page}"),
    "wiktionary":    wiki_link("https://en.wiktionary.org/wiki/{page}"),
    "wikt":          wiki_link("https://en.wiktionary.org/wiki/{page}"),

    # Meta and mediawiki
    "m":             wiki_link("https://meta.wikimedia.org/wiki/{page}"),
    "meta":          wiki_link("https://meta.wikimedia.org/wiki/{page}"),
    "mw":            wiki_link("https://mediawiki.org/wiki/{page}"),

    # Other
    "g":             wiki_link("https://google.com/search?q={page}", delimiter="+"),
    "google":        wiki_link("https://google.com/search?q={page}", delimiter="+"),
}


class Link:
    def __init__(self, match: re.Match, wiki: Wiki) -> None:
        self.target: str = match.group(1)
        self.title: Optional[str] = match.group(2)

        if self.title == "":
            self.title = self.target.split(":")[-1]
        if self.title is None:
            self.title = self.target

        self.wiki = wiki
        self.original = match.group(0)
        self.url = self.make_url()
    
    def make_url(self) -> str:
        for prefix, func in PREFIXES.items():
            if self.target.startswith(prefix):
                return func(self.target[len(prefix) + 1:])

        return self.wiki.url_to(self.target)

    def __repr__(self):
        return f"<Link target={self.target} title={self.title} url={self.url}>"

    def to_hyperlink(self) -> str:
        return f"[{self.title}](<{self.url}>)"

    def to_link(self) -> str:
        return f"<{self.url}>"


class Wikilinks(commands.Cog):
    """Преобразовывает [[текст в квадратных скобках]] в ссылки на статьи на вики."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def find_wikilinks(self, ctx: WhiteContextBase) -> List[Link]:
        text = ctx.message.content
        codeblock_matches = list(CODEBLOCK_REGEX.finditer(text))
        link_matches = list(WIKILINK_REGEX.finditer(text))
        if len(link_matches) == 0:
            return []

        await ctx.settings.query_wiki_info() # type: ignore

        links = []
        for link in link_matches:
            is_within_codeblock = False
            
            for match in codeblock_matches:
                if link.start(0) > match.start(0) and link.end(0) < match.end(0):
                    is_within_codeblock = True

            if is_within_codeblock:
                continue
            
            links.append(Link(link, wiki=ctx.wiki))

        return links

    async def create_webhook(self, channel: discord.TextChannel) -> discord.Webhook:
        webhook = await channel.create_webhook(name="Wikilink Manager")

        assert self.bot.pool is not None
        query = """
        INSERT INTO wh_wikilink_webhooks VALUES ($1, $2)
        ON CONFLICT (channel_id) DO UPDATE
        SET webhook_url = excluded.webhook_url
        """
        async with self.bot.pool.acquire() as conn:
            await conn.execute(query, channel.id, webhook.url)
        
        return webhook

    async def get_webhook(self, channel: discord.TextChannel) -> discord.Webhook:
        assert self.bot.pool is not None
        
        query = "SELECT webhook_url FROM wh_wikilink_webhooks WHERE channel_id=$1"
        async with self.bot.pool.acquire() as conn:
            result = await conn.fetchrow(query, channel.id)
        
        if result is None:
            return await self.create_webhook(channel)

        return discord.Webhook.from_url(result["webhook_url"], session=self.bot.session)

    def get_webhook_channel(self, channel: discord.abc.Messageable) -> discord.TextChannel:
        if isinstance(channel, discord.Thread):
            result = channel.parent
        elif isinstance(channel, discord.TextChannel):
            result = channel
        else:
            raise ValueError("Cannot create webhooks in this channel")

        return result # type: ignore

    async def resend_message(self, ctx: WhiteContextBase, content: str, webhook: discord.Webhook) -> None:
        try:
            message = ctx.message
            attrs: Dict[str, Any] = dict(
                content=content,
                files=[
                    await attachment.to_file(spoiler=attachment.is_spoiler()) 
                    for attachment in message.attachments
                ],
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url,
            )
            if isinstance(ctx.channel, discord.Thread):
                attrs["thread"] = ctx.channel
            
            await webhook.send(**attrs)
        except discord.NotFound:
            channel = self.get_webhook_channel(ctx.channel)
            new_webhook = await self.create_webhook(channel)
            await self.resend_message(ctx, content, new_webhook)

    async def send_links(self, channel: discord.abc.Messageable, links: List[Link]) -> discord.Message:
        content = "\n".join(link.to_link() for link in links)
        return await channel.send(content)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if message.guild is None:
            return
        
        ctx = await self.bot.get_context(message)
        links = await self.find_wikilinks(ctx)
        if len(links) == 0:
            return

        channel = self.get_webhook_channel(ctx.channel)
        try:
            webhook = await self.get_webhook(channel)
        except discord.Forbidden:
            await self.send_links(ctx.channel, links)
            return
        
        content = message.content
        for link in links:
            content = content.replace(link.original, link.to_hyperlink(), 1)
        
        try:
            await self.resend_message(
                ctx=ctx,
                content=content,
                webhook=webhook
            )
        except discord.HTTPException:
            await self.send_links(ctx.channel, links)
            return

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send("Упс! Получилось некрасиво, потому что у меня нет права управлять сообщениями. Пожалуйста, выдайте мне его, и я смогу удалить исходное сообщение.")

def setup(bot: Bot) -> None:
    bot.add_cog(Wikilinks(bot))
