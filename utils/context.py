from discord.ext import commands

import slash
from .settings import GuildSettings

class WhiteContextBase:
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
    
class WhiteContext(WhiteContextBase, commands.Context):
    pass

class WhiteInteractionContext(WhiteContextBase, slash.SlashContext):
    pass