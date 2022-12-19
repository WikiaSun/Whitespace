from dataclasses import dataclass
from discord.ext import commands

class WhiteException(Exception):
    pass

class WikiNotFound(WhiteException):
    pass

class PageNotFound(WhiteException):
    pass

class WhiteCommandException(WhiteException, commands.CommandError):
    pass

@dataclass
class MissingRequiredFlag(WhiteCommandException):
    flag: str