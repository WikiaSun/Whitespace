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
    wiki: "Wiki"
    id: Optional[int] = None
    discord_tag: Optional[str] = None

    @property
    def page_url(self):
        return self.wiki.url_to("User:" + self.name)

    @property
    def avatar_url(self):
        return f"https://services.fandom.com/user-avatar/user/{self.id}/avatar"

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: "Account") -> bool:
        return self.name == other.name
    
@dataclass
class Binding:
    fandom_account: Account
    discord_account: discord.abc.Snowflake
    trusted: bool
    active: bool

@dataclass
class User:
    """Represents an user.
    
    The user is a person that can have multiple accounts both on Fandom an Discord.
    """
    _bot: "Bot"
    bindings: List[Binding] = field(default_factory=list)
    
    async def add_account(
        self,
        *,
        guild_id: int,
        fandom_account: Optional[str] = None,
        discord_id: Optional[int] = None,
        trusted: bool = True
    ):
        pass

    @property
    def fandom_accounts(self) -> List[Account]:
        return list(set(b.fandom_account for b in self.bindings))

    @property
    def discord_accounts(self) -> List[discord.abc.Snowflake]:
        return list(set(b.discord_account for b in self.bindings))

class RequirementsCheckResultStatus(enum.Enum):
    ok = True
    failed = False

@dataclass
class RequirementsCheckResult:
    status: RequirementsCheckResultStatus
