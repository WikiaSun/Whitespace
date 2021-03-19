from discord.ext import commands
import discord

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('!'), **kwargs)

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))


bot = Bot()

bot.run("")
