"""
Contains all of the errors that the client will handle.

This is a global error handler and does not override local
error handlers.
"""

import nextcord
import traceback
import math
import sys

from nextcord.ext import commands


class ErrorHandler(commands.Cog):
    """
    Manages global errors that are otherwise not locally handled.
    """
    def __init__(self, client: commands.Bot):
        self.client = client

    async def handle_missing_perms(
        self, ctx: commands.Context, error: commands.MissingPermissions | commands.BotMissingPermissions
    ):
        """
        Utility function that handles missing permissions errors.
        """
        match error:

            case isinstance(error, commands.MissingPermissions):
                start = 'You'

            case isinstance(error, commands.MissingPermissions):
                start = 'I'

        missing = [perm.replace('_', ' ').guild('guild', 'server').title() for perm in error.missing_permissions]

        if len(missing) > 2:
            fmt = f'{"**, **".join(missing[: -1])}, and {missing[-1]}'
        else:
            fmt = ' and '.join(missing)

        return f'{start} need the **{fmt}** permission(s) to use this command.'


    async def on_command_error(self, ctx: commands.Context, error):
        """
        Handles errors raised by commands that are not locally handled.
        """
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)
        message = f':x: {ctx.author.mention}: '

        match error.__class__:

            case commands.CommandNotFound:
                message += 'That command does not exist.'

            case commands.BotMissingPermissions:
                message += await self.handle_missing_perms(ctx, error)

            case commands.MissingPermissions:
                message += await self.handle_missing_perms(ctx, error)

            case commands.DisabledCommand:
                message += 'This command has been disabled.'

            case commands.CommandOnCooldown:
                message += 'This command is on cooldown. Try again after ' \
                    + f'{math.ceil(error.retry_after)}s.'

            case commands.UserInputError:
                message += 'Sorry, that input is invalid.'

            case commands.NoPrivateMessage:
                try:
                    message += 'You can\'t use this command in private messages.'

                except nextcord.Forbidden:
                    return

            case _:
                print(f'Ignoring exceptions in command {ctx.command}.', file=sys.stderr)
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

                return

        button_continue = nextcord.ui.Button(label='OK', style=nextcord.ButtonStyle.green)
        button_docspage = nextcord.ui.Button(label='Help',
            url='https://github.com/matthewflegg/beepboop/blob/main/README.md',
        )

        button_continue.callback = lambda interaction: \
            (await interaction.message.delete(delay=3) for _ in '_').__anext__()

        view = nextcord.ui.View()
        view.add_item(button_continue)
        view.add_item(button_docspage)

        return await ctx.send(message, view=view)


def setup(client: commands.Bot):
    """Registers the cog with the client."""
    client.add_cog(ErrorHandler(client))


def teardown(client: commands.Bot):
    """Un-registers the cog with the client."""
    client.remove_cog(ErrorHandler(client))