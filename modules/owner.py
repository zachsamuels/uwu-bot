from discord.ext import commands
import discord
from utils import errorhandler
import asyncpg
from datetime import datetime
import copy
from typing import Union

class owner:
    def __init__(self, bot):
        self.bot = bot
        self.staff_ids = [246938839720001536, 300088143422685185, 422181415598161921, 311553339261321216]

    async def __local_check(self, ctx):
        if ctx.author.id in self.staff_ids:
           return True

        raise(errorhandler.IsStaff(ctx))

    @commands.command(description="Blacklist a user via ID", brief="Blacklist")
    async def blacklist(self, ctx, user_id:int, *, reason=None):
        if reason is None:
            reason = 'No reason'
        if len(reason) > 512:
            return await ctx.send("Reason can't be more then `512` characters.")

        try:
            await self.bot.pool.execute("INSERT INTO blacklists (user_id, reason) VALUES ($1, $2)", user_id, reason)
            self.bot.blacklisted.append(user_id)
            return await ctx.send(f"Done. Blacklisted `{user_id}` for `{reason}`")
        except asyncpg.UniqueViolationError:
            return await ctx.send("Error. User already blacklisted.", delete_after=30)

    @commands.command(description="Unblacklist a user from their ID", brief="Unblacklist")
    async def unblacklist(self, ctx, user_id:int):
        try:
            await self.bot.pool.execute("DELETE FROM blacklists WHERE user_id = $1", user_id)
            self.bot.blacklisted.remove(user_id)
            return await ctx.send("Done")
        except:
            await ctx.sendz("User not blacklisted.", delete_after=30)

    @commands.group(invoke_without_command=True)
    async def patreon(self, ctx):
        await ctx.send("No subcommand passed. Valid subcommands `add, remove`", delete_after=30)

    @patreon.command()
    async def add(self, ctx, user_id:int, tier):
        if tier not in ['Supporter', 'Awesome', 'Wow']:
            return await ctx.send("Invalid tier. Valid are `Supporter, Awesome, Wow`")

        try:
            await self.bot.pool.execute("INSERT INTO p_users (user_id, tier) VALUES ($1, $2)", user_id, tier)
            self.bot.patrons.append(user_id)
            return await ctx.send("Done")
        except asyncpg.UniqueViolationError:
            return await ctx.send("User already a patron.", delete_after=30)

    @commands.is_owner()
    @commands.command()
    async def die(self, ctx):
        await self.bot.pool.execute("UPDATE commands_used SET commands_used = commands_used + $1", self.bot.commands_ran)
        self.bot.logger.info("[Logout] Logging out...")
        await ctx.send("Bye cruel world...")
        await self.bot.logout()

def setup(bot):
    bot.add_cog(owner(bot))