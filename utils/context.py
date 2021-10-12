from discord.ext import commands

import slash
from .settings import GuildSettings
from .wiki import Wiki

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

    @property
    def wiki(self):
        return Wiki(url=self.settings.bound_wiki_url, session=self.bot.session)
    
class WhiteContext(WhiteContextBase, commands.Context):
    pass

class WhiteInteractionContext(WhiteContextBase, slash.SlashContext):
    pass