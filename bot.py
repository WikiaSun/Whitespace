import discord
from discord.ext import commands

from config import config

def _prefix_callable(bot, msg):
    # Will be implemented later
    return commands.when_mentioned_or(config.default_prefix)(bot, msg)

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=_prefix_callable, **kwargs)

        for cog in config.cogs:
            self.load_extension(cog)

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))


bot = Bot()

bot.run(config.credentials.token)
