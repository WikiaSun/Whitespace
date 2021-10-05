import random
import discord
from discord import ui
from discord.ext import commands
from discord.utils import format_dt

import slash
from config import config

class Info(commands.Cog, name="Информация"):
    def __init__(self, bot):
        self.bot = bot

    @slash.command(aliases=["about", "invite"])
    async def info(self, ctx):
        """Показывает информацию о боте"""
        em = discord.Embed(
            title=f"Приветики, {ctx.author.name}!", 
            description=self.bot.description + "\n\nМои владельцы — Infinity#1806 и Шпик#2212, я написан на языке Python.", 
            colour=config.primary_color
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

    @slash.command(name="random")
    async def random(
        self, 
        ctx, 
        num_start: int = slash.Option(description="Нижняя граница диапазона"),
        num_end: int = slash.Option(description="Верхняя граница диапазона")
    ):
        """Выводит случайное число в диапазоне, указанном в параметрах."""
        await ctx.send(random.randint(num_start, num_end))
    

    @slash.command(name="choice")
    async def random_choice(self, ctx, elements = slash.Option(description="Список элементов для выбора, разделитель — `|`.")):
        """Выбирает случайный элемент из списка."""
        elements = [e.strip() for e in elements.split("|")]
        if len(elements) < 2:
            await ctx.send(f"{config.emojis.error} | Укажите как минимум два варианта.")
            return

        await ctx.send(random.choice(elements))

    @slash.command(name="serverinfo")
    async def guildinfo(self, ctx):
        """Показывает информацию о сервере."""
        em = discord.Embed(colour=89847)
        em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        em.set_thumbnail(url=ctx.guild.icon.url)

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
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Info(bot))

def teardown(bot):
    bot.remove_cog("help")