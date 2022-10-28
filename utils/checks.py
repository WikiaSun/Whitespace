from .errors import MissingRequiredFlag
from .context import WhiteContext

from discord.ext import commands


async def guild_has_flag(ctx: WhiteContext, flag: str) -> bool:
    assert ctx.settings is not None 
    await ctx.settings.query("flags")
    assert ctx.settings.flags is not None
    
    if not getattr(ctx.settings.flags, flag):
        raise MissingRequiredFlag(flag=flag)
    
    return True

def require_flag(flag: str):
    async def pred(ctx: WhiteContext):
        return await guild_has_flag(ctx, flag)
    
    return commands.check(pred)