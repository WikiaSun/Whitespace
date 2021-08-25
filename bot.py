import discord
from discord import ui
from discord.ext import commands
import asyncpg

from config import config
import slash

def _prefix_callable(bot, msg):
    # Will be implemented later
    return commands.when_mentioned_or(config.default_prefix)(bot, msg)

class Bot(slash.SlashBot):
    def __init__(self):
        super().__init__(
            command_prefix=_prefix_callable, 
            description=config.description,
            register_commands_on_startup=not config.debug,
            guild_ids=config.test_guilds if config.debug else None
        )

        for cog in config.cogs:
            self.load_extension(cog)

    async def start(self, *args, **kwargs):
        self.pool = await asyncpg.create_pool()
        await super().start(*args, **kwargs)
    
    async def close(self, *args, **kwargs):
        await self.pool.close()
        await super().close(*args, **kwargs)

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))

    async def on_guild_join(self, guild):
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO wh_guilds (id) VALUES ($1)", str(guild.id))
        

bot = Bot()

@bot.command(name='info', aliases=['invite'])
async def bot_info(ctx):
    """Показывает информацию о боте"""
    em = discord.Embed(
        title=f"Приветики, {ctx.author.name}!", 
        description=bot.description + "\n\nМои владельцы — Infinity#1806 и Шпик#2212, я написан на языке Python.", 
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

bot.run(config.credentials.token)
