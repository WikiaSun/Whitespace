from dataclasses import asdict, dataclass, InitVar
from typing import Optional

from discord.ext import commands

@dataclass
class GuildSettings:
    id: int
    prefix: str

    bot: InitVar[commands.Bot]

    bound_wiki_url: Optional[str] = None

    def __post_init__(self, bot):
        self._bot = bot
        self._pool = bot.pool

    async def query(self, *args):
        if not args:
            to_select = "*"
        else:
            fields = asdict(self).keys()
            for field in args:
                if field not in fields:
                    raise ValueError("Invalid parameter passed: " + field)

            to_select = ", ".join(args)

        query = f"SELECT {to_select} FROM wh_guilds WHERE id=$1"
        async with self._pool.acquire() as conn:
            result = await conn.fetchrow(query, self.id)
        
        for field, value in result.items():
            setattr(self, field, value)
        
        return result

    async def update(self, **kwargs):
        if not kwargs:
            raise ValueError("No values passed")
        
        query = "UPDATE wh_guilds SET "
        fields = asdict(self).keys()
        for idx, field in enumerate(kwargs.keys()):
            if field not in fields:
                raise ValueError("Invalid parameter passed: " + field)

            query += f"{field}=${idx + 1} "
        query += f"WHERE id=${len(kwargs) + 1}"

        async with self._pool.acquire() as conn:
            result = await conn.execute(query, *kwargs.values(), self.id)

        for field, value in kwargs.items():
            setattr(self, field, value)

        return result