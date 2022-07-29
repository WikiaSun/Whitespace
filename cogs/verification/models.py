from dataclasses import dataclass, field
import enum
from typing import TYPE_CHECKING, List, Optional

import discord

if TYPE_CHECKING:
    from bot import Bot
    from utils.wiki import Wiki

@dataclass
class Account:
    name: str
    id: Optional[int]
    discord_tag: str
    wiki: "Wiki"

    @property
    def page_url(self):
        return self.wiki.url_to("User:" + self.name)

    @property
    def avatar_url(self):
        return f"https://services.fandom.com/user-avatar/user/{self.id}/avatar"
    

@dataclass
class User:
    """Represents an user.
    
    The user is a person that can have multiple accounts both on Fandom an Discord.
    """
    _bot: "Bot"
    fandom_accounts: List[Account] = field(default_factory=list)
    discord_accounts: List[discord.abc.Snowflake] = field(default_factory=list)

    async def add_account(
        self,
        *,
        guild_id: int,
        fandom_account: Optional[str] = None,
        discord_id: Optional[int] = None,
        trusted: bool = True
    ):
        pass

class RequirementsCheckResultStatus(enum.Enum):
    ok = True
    failed = False

@dataclass
class RequirementsCheckResult:
    status: RequirementsCheckResultStatus
