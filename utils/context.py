from typing import TYPE_CHECKING, Optional
import discord
from discord.ext import commands

from .settings import GuildSettings
from .wiki import Wiki

if TYPE_CHECKING:
    from ..bot import Bot

class WhiteContext(commands.Context):
    bot: "Bot"
    guild: Optional[discord.Guild]
    settings: Optional[GuildSettings]

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
        if self.guild is None:
            raise commands.CommandError("Settings only exist on guilds.")

        # if guild is not None, settings are set
        return Wiki(url=self.settings.bound_wiki_url, session=self.bot.session) # type: ignore
