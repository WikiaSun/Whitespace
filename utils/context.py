import asyncio
from discord.ext import commands

import slash
from .settings import GuildSettings
from .wiki import Wiki

class WhiteContextBase(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.guild:
            self.settings = GuildSettings(
                id=self.guild.id,
                prefix=self.bot.prefixes[self.guild.id],
                bot=self.bot
            )
        else:
            self.settings = None

    @property
    def wiki(self):
        return Wiki(url=self.settings.bound_wiki_url, session=self.bot.session)
    
class WhiteContext(WhiteContextBase, commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.responded = asyncio.Event()

    async def send(self, *args, **kwargs):
        self.responded.set()
        return await super().send(*args, **kwargs)

    async def type_until_response(self):
        async with self.typing():
            await self.responded.wait()

    async def defer(self, ephemeral=False):
        asyncio.create_task(self.type_until_response())

class WhiteInteractionContext(WhiteContextBase, slash.SlashContext):
    pass