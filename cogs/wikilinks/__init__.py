from .cog import Wikilinks
from bot import Bot

__all__ = ("setup",)

async def setup(bot: Bot) -> None:
    await bot.add_cog(Wikilinks(bot))