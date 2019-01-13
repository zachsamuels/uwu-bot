import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import traceback
import asyncio
import asyncpg
import yaml  # removed aiofiles because its not needed
from datetime import datetime
import os
import sys
import logging
import aiohttp
import aioredis
import psutil
import discord
import logging.handlers

logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)
handler = logging.handlers.TimedRotatingFileHandler(filename=f'bot.log', encoding='utf-8', when="D", interval=1, utc=True, backupCount=10)
handler.setFormatter(logging.Formatter('[%(asctime)s:%(levelname)s:%(name)s] %(message)s'))
logger.addHandler(handler)

try:
    import uvloop
except ImportError:
    if sys.platform == "linux":  # alert the user to install uvloop if they are on a linux system
        print("UVLoop not detected")
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

description = """uwu. A RPG bot made by mellowmarshe#0001"""

startup_extensions = ['jishaku',
                      'utils.errorhandler',
                      'modules.create',
                      'modules.exploring',
                      'modules.owner',
                      'modules.uwulonian',
                      'modules.misc',
                      'modules.patron',
                      'modules.DBL',
                      'modules.marriage',
                      'modules.uwus',
                      'modules.events',
                      'modules.daily',
                      'modules.pets',
                      'modules.help',
                      'modules.votes',
                      'modules.logging']

prefixes = ['uwu ', '|']

class uwu(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(*prefixes), case_insensitive=True, description=description, reconnect=True)
        self.launch_time = datetime.utcnow()
        self.config = yaml.load(open("config.yml"))
        self.pool = None  # pool is unset till the bot is ready
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.bot_version = '1.0.3 oWo'
        self.process = psutil.Process(os.getpid())
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger('bot')
        self.blacklisted = []
        self.patrons = []
        self.add_check(self.global_cooldown)

    map = commands.CooldownMapping.from_cooldown(1, 4, commands.BucketType.user)

    async def global_cooldown(self, ctx: commands.Context):
        bucket = self.map.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        else:
            return True

    async def start(self):
        await self.create_pool()
        for ext in startup_extensions:
            try:
                self.load_extension(ext)
            except BaseException as e:
                print(f"Failed to load {ext}\n{type(e).__name__}: {e}")
        await super().start(self.config['token'])

    async def create_pool(self):
        credentials = {"user": self.config['dbuser'], "password": self.config['dbpassword'],"database": self.config['dbname'], "host": "127.0.0.1"}
        self.pool = await asyncpg.create_pool(**credentials, max_size=100)

    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        await self.process_commands(after)

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content == self.user.mention:
            return await message.channel.send("I'm uwu! My prefix is `uwu `. For commands do `uwu help`.")

        ctx = await self.get_context(message)

        if ctx.command:
            if message.author.id in self.blacklisted:
                return await message.channel.send(f"You may not use uwu. You were blacklisted.")

            await self.invoke(ctx)

    async def on_ready(self):
        await self.create_pool()
        self.redis = await aioredis.create_redis_pool('redis://localhost', password=self.config['redispassword'], minsize=5, maxsize=10, loop=self.loop)
        with open("utils/schema.sql") as f:
            await self.pool.execute(f.read())
        print("Bot ready!")
        bl_users = await self.pool.fetch("SELECT * FROM blacklists")
        patrons = await self.pool.fetch("SELECT * FROM p_users")
        for i in range(len(bl_users)):
            self.blacklisted.append(bl_users[i]['user_id'])
        self.logger.info(f"[Start] Blacklisted users added.")
        for i in range(len(patrons)):
            self.patrons.append(patrons[i]['user_id'])
        self.logger.info(f"[Start] Patrons added.")
        game = discord.Game("with fwends")
        await self.change_presence(status=discord.Status.dnd, activity=game)
        self.logger.info(f"[Start] Bot started with {len(self.guilds)} guilds and {len(self.users)} users.")

    async def on_command_completion(self, ctx):
        await self.pool.execute("UPDATE commands_used SET commands_used = commands_used + 1;")

    async def on_message_delete(self, message):
        content = message.content 
        msg_type_o = 0
        if message.attachments:
            content = message.attachments[0].proxy_url
            msg_type_o = 1
        if message.embeds:
            content = message.embeds[0].description
            msg_type_o = 2
        try:
            await self.pool.execute("""INSERT INTO del_snipe (guild_id, user_id, channel_id, message, msg_type) VALUES ($1, $2, $3, $4, $5) 
            ON CONFLICT (channel_id) DO UPDATE SET user_id = $2, message = $4, msg_type = $5""", message.guild.id, message.author.id, message.channel.id, content, msg_type_o)
        except:
            pass

    async def on_guild_remove(self, guild):
        await self.redis.execute("DECR", "current_guilds")

    async def on_guild_join(self, guild):
        await self.redis.execute("INCR", "current_guilds")

if __name__ == "__main__":
    uwu().run()