import discord
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

bot.run(config.credentials.token)
