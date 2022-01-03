from .cog import Wikilinks
from bot import Bot

__all__ = ("setup",)

def setup(bot: Bot) -> None:
    bot.add_cog(Wikilinks(bot))