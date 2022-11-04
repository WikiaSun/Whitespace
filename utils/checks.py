from discord.ext import commands

from .errors import MissingRequiredFlag
from .context import WhiteContext


async def guild_has_flag(ctx: WhiteContext, flag: str) -> bool:
    assert ctx.settings is not None 
    await ctx.settings.query("flags")
    assert ctx.settings.flags is not None
    
    return getattr(ctx.settings.flags, flag)

async def check_has_flag(ctx: WhiteContext, flag: str) -> bool:
    if not await guild_has_flag(ctx, flag):
        raise MissingRequiredFlag(flag=flag)
    return True

def require_flag(flag: str):
    async def pred(ctx: WhiteContext):
        return await check_has_flag(ctx, flag)

    return commands.check(pred)
    