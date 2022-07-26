from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Dict, List

from discord.ext import commands
import discord

from utils.context import WhiteContext

from .link import Link
if TYPE_CHECKING:
    from bot import Bot


WIKILINK_REGEX = re.compile(r"\[\[(.+?)(?:\|(.*?))?\]\]([^ `\n]+)?")
CODEBLOCK_REGEX = re.compile(r"(`{1,3}).*?\1", re.DOTALL)


class Wikilinks(commands.Cog):
    """Преобразовывает [[текст в квадратных скобках]] в ссылки на статьи на вики."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def find_wikilinks(self, ctx: WhiteContext) -> List[Link]:
        text = ctx.message.content
        codeblock_matches = list(CODEBLOCK_REGEX.finditer(text))
        link_matches = list(WIKILINK_REGEX.finditer(text))
        if len(link_matches) == 0:
            return []

        await ctx.settings.query_wiki_info()  # type: ignore

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

        return result  # type: ignore

    async def resend_message(self, ctx: WhiteContext, content: str, webhook: discord.Webhook) -> None:
        try:
            message = ctx.message

            if (reference := message.reference) is not None and isinstance(reference.resolved, discord.Message):
                msg = f"> Ответ на [сообщение]({reference.jump_url}) от "
                if (author := reference.resolved.author) in message.mentions:
                    msg += author.mention
                else:
                    msg += f"**{author}**"
                msg += "\n\n"

                content = msg + content

            attrs: Dict[str, Any] = dict(
                content=content,
                files=[
                    await attachment.to_file(spoiler=attachment.is_spoiler()) 
                    for attachment in message.attachments
                ],
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url,
                allowed_mentions=discord.AllowedMentions(everyone=False, roles=False)
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
            await ctx.send("Упс! Получилось некрасиво, потому что у меня нет права управлять сообщениями."
                           "Пожалуйста, выдайте мне его, и я смогу удалить исходное сообщение.")
