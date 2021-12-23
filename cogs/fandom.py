from datetime import datetime

import aiohttp
from discord.ext import commands
import discord
from discord.utils import format_dt

from config import config
import slash
from utils.converters import PageConverter, WikiConverter
from utils.errors import WikiNotFound

class Fandom(commands.Cog, name="Фэндом"):
    """Команды для взаимодействия с вики на Фэндоме."""

    def __init__(self, bot):
        self.bot = bot

    @slash.command()
    async def page(
        self,
        ctx,
        wiki: WikiConverter = slash.Option(description="Вики, на которой нужно искать страницу."),
        *,
        name: PageConverter = slash.Option(description="Имя страницы")
    ):
        """Показывает информацию о странице на вики (если не указана, то проверяется вики по умолчанию)."""
        await ctx.defer()
        if wiki is None:
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

    async def cog_command_error(self, ctx, error):
        error = error.original

        if isinstance(error, WikiNotFound):
            await ctx.send(f"{config.emojis.error} | Вики с данным адресом не найдена.")

def setup(bot):
    bot.add_cog(Fandom(bot))
