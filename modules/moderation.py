from discord.ext import commands
import discord
from utils import errorhandler
import asyncpg
from datetime import datetime
import copy
from typing import Union
import inspect
import textwrap
from contextlib import redirect_stdout
import io
import traceback


class moderation:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, prefix: str):
        try:
            if len(prefix) > 512:
                return await ctx.caution(
                    "You can't have a prefix with more than 512 characters."
                )
            if self.bot.prefixes.get(ctx.guild.id):
                await self.bot.pool.execute(
                    "UPDATE guild_prefixes SET prefix = $1 WHERE guild_id = $2",
                    prefix,
                    ctx.guild.id,
                )
            else:
                await self.bot.pool.execute(
                    "INSERT INTO guild_prefixes (guild_id, prefix) VALUES ($1, $2)",
                    ctx.guild.id,
                    prefix,
                )
            self.bot.prefixes[ctx.guild.id] = prefix
            await ctx.send(f"Set guild prefix to `{prefix}`.")
        except Exception as e:
            await ctx.send(e)


def setup(bot):
    bot.add_cog(moderation(bot))
