from typing import Dict
import aiohttp
import discord
from discord.ext import commands
import asyncpg

from config import config
from utils.context import WhiteContext
from utils.errors import MissingRequiredFlag

def _prefix_callable(bot, msg):
    if not msg.guild:
        prefix = config.default_prefix
    else:
        prefix = bot.prefixes[msg.guild.id]

    return commands.when_mentioned_or(prefix)(bot, msg)

class Bot(commands.Bot):
    pool: asyncpg.Pool
    prefixes: Dict[int, str]

    def __init__(self):
        intents = discord.Intents(
            guilds=True,
            messages=True,
            message_content=True,
            members=True
        )
        allowed_mentions = discord.AllowedMentions(
            everyone=False, 
            roles=False
        )
        if config.debug:
            self.guild_ids = config.test_guilds
        else:
            self.guild_ids = None
            
        super().__init__(
            command_prefix=_prefix_callable,
            intents=intents,
            allowed_mentions=allowed_mentions,
            description=config.description,
        )

    async def sync(self):
        if self.guild_ids:
            for guild_id in self.guild_ids:
                guild = discord.Object(guild_id)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def setup_hook(self):
        self.pool = await asyncpg.create_pool() # type: ignore # idk why it's Pool | None
        self.session = aiohttp.ClientSession()

        self.prefixes = await self.get_prefixes()

        for cog in config.cogs:
            await self.load_extension(cog)

    async def close(self, *args, **kwargs):
        await self.pool.close()
        await self.session.close()
        
        await super().close(*args, **kwargs)

    async def get_context(self, origin, cls=WhiteContext) -> WhiteContext:
        return await super().get_context(origin, cls=cls)

    async def get_prefixes(self) -> Dict[int, str]:
        guilds = await self.pool.fetch("SELECT id, prefix FROM wh_guilds")
        return {
            g["id"]: g["prefix"]
            for g in guilds
        }

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))

    async def on_guild_join(self, guild):
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO wh_guilds (id) VALUES ($1)", str(guild.id))

    async def on_command_error(self, ctx: WhiteContext, error: commands.CommandError) -> None:
        unwrapped = error
        while original := getattr(unwrapped, "original", None):
            unwrapped = original
        
        if isinstance(unwrapped, MissingRequiredFlag):
            if unwrapped.flag.startswith("beta"):
                text = "Эта команда находится в бета-тестировании. Попросите администраторов сервера включить соответствующую ей функцию в настройках."
            else:
                text = "На вашем сервере отключен доступ к этой функции"
            await ctx.send(f"{config.emojis.error} | {text}", ephemeral=True)
        else:
            raise error
        

bot = Bot()

if __name__ == "__main__":
    bot.run(config.credentials.token)
