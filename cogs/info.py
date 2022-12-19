from datetime import datetime
import io
import random
from typing import TYPE_CHECKING

import aiohttp
import discord
from discord import ui, app_commands
from discord.ext import commands
from discord.utils import format_dt

from config import config
from utils.checks import check_has_flag
from utils.errors import PageNotFound
from utils.wiki import Wiki, WikiNotFound
from utils.api_data import WikiHub
from utils import converters

if TYPE_CHECKING:
    from ..bot import Bot
    from utils.context import WhiteContext

class Info(commands.Cog, name="Информация"):
    def __init__(self, bot: "Bot"):
        self.bot = bot

    async def cog_check(self, ctx: "WhiteContext") -> bool:
        if ctx.guild is None:
            return True
        
        return await check_has_flag(ctx, "beta_info_commands_enabled")
    
    @commands.hybrid_command(name="about")
    async def about(self, ctx: "WhiteContext"):
        """Показывает информацию о боте"""
        em = discord.Embed(
            title=f"Приветики, {ctx.author.name}!", 
            description=self.bot.description + "\n\nМои владельцы — Infinity#1806 и Шпик#2212, я написан на языке Python.", 
            color=config.primary_color
        )
        em.add_field(
            name="Версия", 
            value="""Версия Discord.py: `v{}`
            \nВерсия бота: `v3.0.0.a` (последнее обновление: недавно)
            """.format(discord.__version__)
        )
        em.add_field(
            name='Благодарности', 
            value="""· Спасибо автору замечательной библиотеки discord.py (Danny#0007), без которого данного бота бы не существовало. 
            \n· Спасибо участнику Rrkkm#2006 за создание аватарки для бота 
            \n· Спасибо всем, кто активно тестирует бота и помогает найти ошибки. Благодаря вам он становится лучше.
            """
        )
        em.set_thumbnail(url='https://vignette.wikia.nocookie.net/plutonian-test-lab/images/4/4e/Bot_img.png/revision/latest?cb=20200417104558&format=original&path-prefix=ru')
        
        bot_info_view = ui.View()
        bot_info_view.add_item(ui.Button(label="Пригласить бота", url="https://discord.com/api/oauth2/authorize?client_id=509427930233831444&permissions=939871331&scope=bot%20applications.commands"))
        bot_info_view.add_item(ui.Button(label="Сервер поддержки", url="https://discord.gg/GVvAmTh"))
        await ctx.send(embed=em, view=bot_info_view)

    @commands.hybrid_command(name="random")
    @app_commands.describe(
        num_start="Нижняя граница диапазона",
        num_end="Верхняя граница диапазона"
    )
    async def random(self, ctx: "WhiteContext", num_start: int, num_end: int):
        """Выводит случайное число в диапазоне, указанном в параметрах."""
        await ctx.send(str(random.randint(num_start, num_end)))
    
    @commands.hybrid_command(name="choice")
    @app_commands.describe(
        elements="Список элементов для выбора, разделитель — `|`."
    )
    async def random_choice(self, ctx, elements: str):
        """Выбирает случайный элемент из списка."""
        elements_list = [e.strip() for e in elements.split("|")]
        if len(elements_list) < 2:
            await ctx.send(f"{config.emojis.error} | Укажите как минимум два варианта.")
            return

        await ctx.send(random.choice(elements_list))

    @commands.hybrid_group(name="info")
    async def info(self, ctx: "WhiteContext"):
        if ctx.interaction is None:
            await ctx.invoke(self.about)
    
    @info.command(name="server")
    @commands.guild_only()
    async def guildinfo(self, ctx: "WhiteContext"):
        """Показывает информацию об этом сервере."""
        assert ctx.guild is not None

        em = discord.Embed(colour=89847)
        icon_url = getattr(ctx.guild.icon, "url", None)
        em.set_author(name=ctx.guild.name, icon_url=icon_url)
        em.set_thumbnail(url=icon_url)

        text_channels = 0
        voice_channels = 0
        for c in ctx.guild.channels:
            if isinstance(c, discord.TextChannel):
                text_channels += 1
            elif isinstance(c, discord.VoiceChannel):
                voice_channels += 1

        if ctx.guild.afk_channel:
            afk = ctx.guild.afk_channel.name
        else:
            afk = "Нет"

        if ctx.guild.verification_level == discord.VerificationLevel.none:
            vlevel = "Нет"
        elif ctx.guild.verification_level == discord.VerificationLevel.low:
            vlevel = "Низкий"
        elif ctx.guild.verification_level == discord.VerificationLevel.medium:
            vlevel = "Средний"
        elif ctx.guild.verification_level == discord.VerificationLevel.high:
            vlevel = "Высокий"
        else:
            vlevel = "Очень высокий"

        em.add_field(
            name="Каналы", 
            value=f"""**{text_channels}** текстовых, **{voice_channels}** голосовых
            АФК канал: **{afk}**
            """,
            inline=True
        )
        em.add_field(
            name="Участники и роли", 
            value=f"""**{ctx.guild.member_count}** участников
            Владелец: <@!{ctx.guild.owner_id}>
            **{len(ctx.guild.roles) - 1}** ролей
            """,
            inline=True
        )
        em.add_field(
            name="Создан", 
            value=format_dt(ctx.guild.created_at), 
            inline=False
        )
        em.add_field(
            name="Прочее",
            value=f"""**{len(ctx.guild.emojis)}** кастомных эмодзи
            Уровень проверки: **{vlevel}**
            """,
            inline=True
        )
        if await self.bot.is_owner(ctx.author):
            assert ctx.settings is not None
            
            await ctx.settings.query("flags")
            assert ctx.settings.flags is not None
            flags = []
            for name, value in ctx.settings.flags:
                if value:
                    flags.append(name)
            
            if flags:
                em.add_field(
                    name="Internal",
                    value=f"""Flags: `{'`, `'.join(flags)}`""",
                    inline=False
                )
        
        await ctx.send(embed=em)
    
    @info.command()
    async def wiki(
        self,
        ctx: "WhiteContext",
        *,
        wiki: Wiki = commands.param(converter=converters.WikiConverter)
    ):
        """Показывает информацию об определённой вики.
        
        Аргументы:
            wiki: Название вики или её адрес в формате ru.community
        """
        await ctx.defer()
        data = await wiki.fetch_data()
        
        em = discord.Embed(
            description=data.description,
            color=1437552
        )
        em.set_author(
            name=data.name, 
            url=data.url, 
            icon_url=data.favicon_url
        )
        em.set_image(url=data.wordmark_url)

        match data.hub:
            case WikiHub.comics:
                hub = "Комиксы"
            case WikiHub.tv:
                hub = "ТВ"
            case WikiHub.movies:
                hub = 'Кино'
            case WikiHub.books:
                hub = 'Книги'
            case WikiHub.gaming:
                hub = 'Игры'
            case ( WikiHub.lifestyle 
                 | WikiHub.travel 
                 | WikiHub.creative 
                 | WikiHub.toys 
                 | WikiHub.education ):
                hub = "Увлечения"
            case WikiHub.other:
                hub = "Другое"
            case _:
                hub = "Неизвестно"

        em.add_field(name="Хаб", value=hub, inline=True)
        em.add_field(name="ID", value=data.id, inline=True)
        em.add_field(name="Дата основания", value=discord.utils.format_dt(data.creation_date), inline=True)
        
        em.add_field(name='Статистика', value=(
			f'**Статей**: {data.article_count}\n'
			f'**Страниц**: {data.page_count}\n'
			f'**Изображений**: {data.image_count}\n'
			f'**Правок**: {data.revision_count}\n'
		), inline=True)
        em.add_field(name='\u200B', value=(
			f'**Сообщений в обсуждениях**: {data.post_count}\n'
			f'**Активных участников**: {data.user_count}\n'
			f'**Администраторов**: {data.admin_count}'
		), inline=True)

        await ctx.send(embed=em)
    
    @info.command()
    async def page(
        self,
        ctx: "WhiteContext",
        wiki: Wiki = commands.param(converter=converters.WikiConverter),
        *,
        name: str = commands.param(converter=converters.PageConverter)
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
        
        data = await wiki.fetch_page_data(name)
        
        em = discord.Embed(
            title=data.name,
            url=wiki.url_to(name), 
            description=data.description, 
            color=0xe35ff5
        )
        edit_date = format_dt(data.last_revision_date)
        em.add_field(
            name="Последняя правка", 
            value="{edit_date} от [{user}]({profile}) ([разн.]({diff}) | [история]({history}))".format(
                edit_date=edit_date,
                user=data.last_revision_author,
                profile=wiki.url_to("User:" + data.last_revision_author),
                diff=wiki.diff_url(data.last_revision_id),
                history=wiki.url_to(name, action="history")
            )
        )
        if data.thumbnail:
            em.set_thumbnail(url=data.thumbnail)

        em.set_footer(text=f"ID: {data.id}")
        await ctx.send(embed=em)

    @page.error
    @wiki.error
    async def page_error(self, ctx: "WhiteContext", error: commands.CommandError):
        unwrapped = error
        while original := getattr(unwrapped, "original", None):
            unwrapped = original
        
        if isinstance(unwrapped, WikiNotFound):
            await ctx.send(
                f"{config.emojis.error} | Вики с данным адресом не найдена. Обратите внимание, адрес вики надо указывать в формате `языковой_код.название`, например `ru.community`.",
                ephemeral=True
            )
        elif isinstance(unwrapped, PageNotFound):
            await ctx.send(f"{config.emojis.error} | Страница с данным адресом не найдена.", ephemeral=True)
    

async def setup(bot: "Bot"):
    await bot.add_cog(Info(bot))

async def teardown(bot: "Bot"):
    await bot.remove_cog("info")