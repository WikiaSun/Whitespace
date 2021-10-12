from discord.ext import commands
import asyncpg

from config import config
import slash
from utils.settings import GuildSettings

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

    async def load_guild_settings(self):
        guilds = await self.pool.fetch("SELECT id, prefix FROM wh_guilds")
        self.settings = {
            g["id"]: GuildSettings(**dict(g), bot=self)
            for g in guilds
        }
    
    async def start(self, *args, **kwargs):
        self.pool = await asyncpg.create_pool()
        await self.load_guild_settings()
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
bot.run(config.credentials.token)
