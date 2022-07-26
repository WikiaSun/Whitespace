from datetime import datetime
from typing import TYPE_CHECKING

import aiohttp
from discord.ext import commands
import discord
from discord.utils import format_dt

from config import config
from utils.converters import PageConverter, WikiConverter
from utils.errors import WikiNotFound
from utils.wiki import Wiki

if TYPE_CHECKING:
    from utils.context import WhiteContext

class Fandom(commands.Cog, name="Фэндом"):
    """Команды для взаимодействия с вики на Фэндоме."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def page(
        self,
        ctx: "WhiteContext",
        wiki: Wiki = commands.param(converter=WikiConverter),
        *,
        name: str = commands.param(converter=PageConverter)
    ):
        """Показывает информацию о странице на вики (если не указана, то проверяется вики по умолчанию).
        
        Аргументы:
            wiki: Вики, на которой нужно искать страницу
            name: Имя страницы
        """
        await ctx.defer()
        if wiki is None:
            if ctx.settings is None:
                wiki = Wiki.from_dot_notation("ru.community", session=ctx.bot.session)
            else:
                await ctx.settings.query_wiki_info()
                wiki = ctx.wiki
        
        try:
            data = await wiki.query_nirvana(
                controller="ArticlesApiController",
                method="getDetails",
                titles=name.replace(" ", "_"),
                abstract=500
            )
        except aiohttp.ContentTypeError as exc:
            raise WikiNotFound from exc

        try:
            data = list(data["items"].values())[0]
        except IndexError:
            await ctx.send(":warning: Данной страницы не существует. Выполняю поиск...")
            return
        
        em = discord.Embed(
            title=data["title"],
            url=wiki.url_to(name), 
            description=data["abstract"], 
            color=0xe35ff5
        )
        edit_date = format_dt(datetime.fromtimestamp(int(data['revision']['timestamp'])))
        em.add_field(
            name="Последняя правка", 
            value="{edit_date} от [{user}]({profile}) ([разн.]({diff}) | [история]({history}))".format(
                edit_date=edit_date,
                user=data['revision']['user'],
                profile=wiki.url_to("User:" + data['revision']['user']),
                diff=wiki.diff_url(data['revision']['id']),
                history=wiki.url_to(name, action="history")
            )
        )
        if data["thumbnail"]:
            em.set_thumbnail(url=data["thumbnail"])
        em.set_footer(text=f"ID: {data['id']}")
        await ctx.send(embed=em)

    @page.error
    async def page_error(self, ctx, error: commands.CommandError):
        unwrapped = error
        while original := getattr(unwrapped, "original", None):
            unwrapped = original
        
        if isinstance(unwrapped, WikiNotFound):
            await ctx.send(f"{config.emojis.error} | Вики с данным адресом не найдена.")
        else:
            raise error

async def setup(bot: commands.Bot):
    await bot.add_cog(Fandom(bot))
