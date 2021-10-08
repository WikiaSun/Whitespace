from dataclasses import asdict, dataclass, InitVar
from typing import Optional

from discord.ext import commands

@dataclass
class WhiteGuild:
    id: int
    prefix: str

    bot: InitVar[commands.Bot]

    bound_wiki_url: Optional[str] = None

    def __post_init__(self, bot):
        self._bot = bot
        self._pool = bot.pool

    async def update(self, **kwargs):
        if not kwargs:
            raise ValueError("No values passed")
        
        query = "UPDATE wh_guilds SET "
        for idx, field in enumerate(kwargs.keys()):
            if field not in asdict(self).keys():
                raise ValueError("Invalid parameter passed: " + field)

            query += f"{field}=${idx + 1}"
        query += f" WHERE id=${len(kwargs) + 1}"

        async with self._pool.acquire() as conn:
            result = await conn.execute(query, *kwargs.values(), self.id)

        return result