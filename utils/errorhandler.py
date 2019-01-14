
import sys
from discord.ext import commands
import discord

caution = '<:caution:521002590566219776>'

def on_cooldown():
    async def predicate(ctx):
        user_cooldown = await ctx.bot.redis.pttl(f"{ctx.author.id}-{ctx.command.qualified_name}")
        if user_cooldown == -2:
            return True

        raise commands.CommandOnCooldown(retry_after= user_cooldown / 1000, cooldown=None)

    return commands.check(predicate)

def has_uwulonian():
    async def predicate(ctx):
        if await ctx.bot.pool.fetchrow("SELECT user_id FROM user_settings WHERE user_id = $1", ctx.author.id):
           return True

        raise(hasUwU(ctx))

    return commands.check(predicate)

def has_voted():
    async def predicate(ctx):
        if await ctx.bot.redis.execute("GET", f"{ctx.author.id}-vote"):
            return True

        raise (hasVoted(ctx))

    return commands.check(predicate)


class NotPatron(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"{caution} You are not a Patron. You can become one here <https://www.patreon.com/mellOwO>")

class IsStaff(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"{caution} This is a staff only command.")

class isEvent(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"{caution} This is an event staff only command.")

class hasUwU(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"{caution} You need an uwulonian for this command.")

class hasVoted(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"{caution} You haven't voted. You can vote here <https://discordbots.org/bot/508725128427995136/vote>. If you voted give me a few seconds to register it.")

class isBeta(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"{caution} This is a beta-server only command.")

class errorhandler:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        errors = (commands.NoPrivateMessage, commands.CommandInvokeError, commands.UserInputError)
        c_errors = (NotPatron, IsStaff, hasUwU, isBeta, isEvent, hasVoted)
        error = getattr(error, 'original', error)

        if isinstance(error, errors):
            await ctx.send(error, delete_after=30)
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{caution} Invalid argument. Did you type it correct?", delete_after=30)
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(f"{caution} Too many arguments. Try less?", delete_after=30)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{caution} Required argument `{str(error.param).split(':')[0]}` is missing. Ya sure you read the command description?", delete_after=30)
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(f"{caution} {ctx.command} is disabled.", delete_after=30)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{caution} I need the permission {error.missing_perms[0]}. You can check my role or channel overrides to find permissions.", delete_after=30)
        elif isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"{caution} You are on cooldown for `{hours}`h `{minutes}`m `{seconds}`sec", delete_after=30)
        elif isinstance(error, c_errors):
            return await ctx.send(error, delete_after=30)
        else:
            print(error)

def setup(bot):
    bot.add_cog(errorhandler(bot))