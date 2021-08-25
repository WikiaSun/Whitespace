import discord
from discord.ext import commands
import slash
from config import config

class WhiteHelp(slash.MinimalHelpCommand):
    def __init__(self):
        super().__init__(
            commands_heading="Команды",
            aliases_heading="Синонимы", 
            no_category="Без категории", 
            verify_checks=False,
            command_attrs=dict(help="Показывает справку бота.")
        )
    
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(title="Справка", description=page, color=config.primary_color)
            await destination.send(embed=embed)

    def get_opening_note(self):
        command_name = self.invoked_with
        return "Наберите `{0}{1} [команда]`, чтобы узнать больше о команде.\n" \
               "Используйте также `{0}{1} [категория]` для информации о категории команд.".format(self.context.clean_prefix, command_name)

    def get_ending_note(self):
        return "Остались вопросы или нужна помощь? Присоединяйтесь к серверу поддержки бота: https://discord.gg/GVvAmTh."
    
    def get_command_signature(self, command):
        fmt = '`{0}{1} {2}`' if command.signature else '`{0}{1}`'
        return fmt.format(self.context.clean_prefix, command.qualified_name, command.signature)

    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            joined = '\u2002'.join(f"`{c.name}`" for c in commands)
            self.paginator.add_line(f'**{heading}**: {joined}')

    def add_command_formatting(self, command):
        super().add_command_formatting(command)

        if isinstance(command, slash.SlashCommand) and command.clean_params:
            self.paginator.add_line("**Аргументы**")
            for name, param in command.clean_params.items():
                param_name = param.default.name or name
                self.paginator.add_line(f"`{param_name}` \N{EM DASH} {param.default.description}")

    def add_subcommand_formatting(self, command):
        fmt = '`{0}{1}` \N{EM DASH} {2}' if command.short_doc else '`{0}{1}`'
        self.paginator.add_line(fmt.format(self.context.clean_prefix, command.qualified_name, command.short_doc))
    
    async def send_cog_help(self, cog):
        bot = self.context.bot
        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        note = self.get_opening_note()
        if note:
            self.paginator.add_line(note, empty=True)

        if cog.description:
            self.paginator.add_line(cog.description, empty=True)

        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        if filtered:
            self.paginator.add_line(f'**Команды модуля «{cog.qualified_name}»**')
            for command in filtered:
                self.add_subcommand_formatting(command)

            note = self.get_ending_note()
            if note:
                self.paginator.add_line()
                self.paginator.add_line(note)
        
        await self.send_pages()

    def command_not_found(self, string):
        return 'Команды `{}` не существует.'.format(string)

    def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return 'У команды `{0.qualified_name}` нет подкоманды `{1}`.'.format(command, string)
        return 'У команды `{0.qualified_name}` нет подкоманд.'.format(command)

    async def command_callback(
        self, 
        ctx,
        *, 
        command = slash.Option(description="Команда или модуль, для которого необходимо показать справку")
    ):
        return await super().command_callback(ctx, command=command)

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = WhiteHelp()
        self.bot = bot

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

def setup(bot):
    bot.add_cog(HelpCog(bot))

def teardown(bot):
    bot.remove_cog("help")