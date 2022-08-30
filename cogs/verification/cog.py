from typing import TYPE_CHECKING, Optional
import discord
from discord.ext import commands

from utils.wiki import Wiki

from .errors import AlreadyVerified, OwnershipNotProved, RequirementsNotSatsified
from .models import Account, Binding, RequirementsCheckResult, RequirementsCheckResultStatus, User
from config import config, strings as _strings
from utils.converters import AccountConverter

if TYPE_CHECKING:
    from bot import Bot
    from utils.context import WhiteContext

strings = _strings.verification

class Verification(commands.Cog):
    def __init__(self, bot: "Bot"):
        self.bot = bot
    
    async def fetch_user_from_db(
        self,
        fandom_name: Optional[str] = None, 
        discord_id: Optional[int] = None,
        trusted_only: bool = True
    ) -> Optional["User"]:
        """Fetches fandom-discord bindings from the database and returns Account object with that data.
        
        Arguments:
            fandom_name (Optional[str]): Account name on Fandom
            discord_id (Optional[int]): Account id on Discord
            trusted_only (bool): Whether to fetch only trusted bindings

        Returns:
            An User object or None when no bindings satsify the given parameters.
        """
        conditions = []
        args = []
        if fandom_name is not None:
            conditions.append(f"fandom_name = ${len(conditions) + 1}")
            args.append(fandom_name)
        if discord_id is not None:
            conditions.append(f"discord_id = ${len(conditions) + 1}")
            args.append(discord_id)
        if trusted_only:
            conditions.append(f"trusted = true")

        async with self.bot.pool.acquire() as conn:
            results = await conn.fetch(f"""
                WITH RECURSIVE tmp AS (
                    SELECT * 
                    FROM users
                    WHERE {" AND ".join(conditions)}
                    UNION
                        SELECT users.fandom_name, users.discord_id, users.guild_id, users.trusted, users.active
                        FROM users
                        JOIN tmp ON users.fandom_name = tmp.fandom_name or users.discord_id = tmp.discord_id
                        {"WHERE users.trusted = true" if trusted_only else ""}
                ) SELECT * FROM tmp;
           """, *args)
        
        if len(results) == 0:
            return None
        
        bindings = [
            Binding(
                fandom_account=Account(name=result["fandom_name"], wiki=Wiki.from_dot_notation("ru.c")),
                discord_account=discord.Object(id=result["discord_id"]),
                trusted=result["trusted"],
                active=result["active"]
            ) for result in results
        ]
        return User(_bot=self.bot, bindings=bindings)

    async def is_verified(self, ctx: "WhiteContext", member: discord.Member) -> bool:
        """Checks whether the given account is verified in the given context.
        
        Arguments:
            ctx (WhiteContext): The context to check in
            member (discord.Member): The member to check

        Returns:
            True if the account is verified, False otherwise.
        """
        pass

    async def check_requirements(self, ctx: "WhiteContext", user: User) -> RequirementsCheckResult:
        """Checks whether the user satsifies verification requirements in the given context.
        
        Arguments:
            ctx (WhiteContext): The context to check requirements in
            user (User): The user to check requirements for

        Returns:
            ReqiurementsCheckResult object.
        """

    async def verify(self, ctx: "WhiteContext", member: discord.Member, account: Account):
        """Verifies the user in the given context under the given account.
        
        This method performs real actions, like giving roles and changing nickname.
        It does not perform any checks or create bindings. It's up to the caller to do so.

        Arguments:
            ctx (WhiteContext): The context
            member (discord.Member): The member to verify
            account (Account): The account that will be used for verification

        Returns:
            None

        Raises:
            MissingPermissions: The bot doesn't have permissions to verify that user.
        """

    @commands.hybrid_command(name="verify")
    @discord.app_commands.guild_only()
    @commands.guild_only()
    async def verify_command(self, ctx: "WhiteContext", *, account: Account = commands.param(converter=AccountConverter)):
        """Верифицирует Вас на сервере.
        
        Аргументы:
            account: Имя Вашего аккаунта на Фэндоме
        """
        await ctx.defer()

        # a few asserts to make type checker happy
        assert isinstance(ctx.author, discord.Member)
        assert ctx.guild is not None

        if await self.is_verified(ctx, ctx.author):
            raise AlreadyVerified()
        
        user = await self.fetch_user_from_db(discord_id=ctx.author.id, trusted_only=True)
        if user is None or account not in user.fandom_accounts:
            if account.discord_tag != str(ctx.author):
                raise OwnershipNotProved()
        
        if user is None:
            user = User(_bot=self.bot)
        await user.add_account(
            fandom_account=account.name,
            discord_id=ctx.author.id,
            guild_id=ctx.guild.id,
            trusted=True
        )

        req_check_result = await self.check_requirements(ctx, user)
        if req_check_result.status is RequirementsCheckResultStatus.failed:
            raise RequirementsNotSatsified(req_check_result)

        await self.verify(ctx, ctx.author, account)

        em = discord.Embed(
            description=strings.verification_successful.format(guild=ctx.guild.name),
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        em.set_author(
            name=account.name, 
            url=account.page_url,
            icon_url=account.avatar_url
        )
        em.add_field(
            name=strings.account_header,
            value=f"{config.emojis.success} {strings.ownership_confirmed}",
        )
        em.add_field(
            name=strings.requirements_header,
            value=f"{config.emojis.success} {strings.requirements_satsified}"
        )
        await ctx.send(embed=em)
        
