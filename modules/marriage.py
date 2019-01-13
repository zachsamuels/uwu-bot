import discord
from discord.ext import commands
from discord.ext.commands import cooldown
from discord.ext.commands.cooldowns import BucketType
import time
import asyncio
import asyncpg
from datetime import datetime, timezone, timedelta
from utils import errorhandler
from random import randint, choice

heartt = '<:heartt:521071307769774080>'
broken_heartt = '<:brokenheartt:521074570707468308>'
caution = '<:caution:521002590566219776>'

class marriage:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        if await self.bot.pool.fetchrow("SELECT user_id FROM user_settings WHERE user_id = $1", ctx.author.id):
           return True

        raise(errorhandler.hasUwU(ctx))

    @commands.command(descritpion="Marry your lover.", brief="Marry someone")
    async def marry(self,ctx,lover: discord.Member=None):
        async with self.bot.pool.acquire() as conn:
            if lover is None or lover is ctx.author:
                return await ctx.send("Trying to marry yourself...", delete_after=30)
            if await conn.fetchrow("SELECT user_id FROM user_settings WHERE user_id = $1",lover.id) is None:
                return await ctx.send(f"{lover.name} does not have an uwulonian.", delete_after=30)
            if await conn.fetchrow("SELECT user1_id, user2_id FROM marriages WHERE user1_id = $1 OR user2_id = $1 OR user1_id = $2 OR user2_id = $2", ctx.author.id, lover.id):
                return await ctx.send("Either you or the person you are trying to marry is already married...", delete_after=30)

            msg = await ctx.send(f"""{lover.name} would you like to marry {ctx.author.name}. Reply "I do" to marry. Reply "No" to decline the marriage. This will timeout after 30 seconds.""")
            def check(amsg):
                return amsg.author == lover
            try:
                choice = await self.bot.wait_for('message', timeout=30, check=check)
            except asyncio.TimeoutError:
                return await msg.edit(content=f"{lover.name} does not want to marry you.")

            if choice.content.lower() == "i do":
                await conn.execute("INSERT INTO marriages (user1_id,user2_id) VALUES ($1,$2)", ctx.author.id, lover.id)
                await msg.delete()
                return await ctx.send(f"{lover.mention} has accepted {ctx.author.mention}'s proposal {heartt}")
            if choice.content.lower() == "no":
                await msg.delete()
                return await ctx.send(f"{ctx.author.mention} your lover ({lover.mention}) declined your marriage! There's a million fish in the sea though.")
            else:
                await msg.edit(content="Invalid choice. Did you type it properly?", delete_after=30)

    @commands.command(description="Divorce...", brief="Divorce")
    async def divorce(self, ctx):
        async with self.bot.pool.acquire() as conn:
            if await conn.fetchrow("SELECT user1_id, user2_id FROM marriages WHERE user1_id = $1 OR user2_id = $1",ctx.author.id) is None:
                return await ctx.send("You can't divorce someone you're not married to.", delete_after=30)

            await self.bot.pool.execute("DELETE FROM marriages WHERE user1_id = $1 OR user2_id = $1", ctx.author.id)
            await self.bot.pool.execute("DELETE FROM children WHERE lover1_id = $1 OR lover2_id = $1", ctx.author.id)
            await ctx.send(broken_heartt)

    @commands.command(description="Check who you are married to", brief="Check who you married")
    async def marriage(self, ctx):
        married = await self.bot.pool.fetchrow("SELECT user1_id, user2_id, time_married FROM marriages WHERE user1_id = $1 OR user2_id = $1", ctx.author.id)
        if married is None:
            return await ctx.send("You are not married.", delete_after=30)

        if married['user1_id'] == ctx.author.id:
            user = self.bot.get_user(married['user2_id'])
        else:
            user = self.bot.get_user(married['user1_id'])

        marriage_time = datetime.now(timezone.utc) - married['time_married']
        await ctx.send(f"""You have been married to {user.name} since {married['time_married'].strftime("%X at %x")} ({marriage_time.days}d).""")

    @commands.command(descritpion="Breed with your lover", aliases=['sex', 'fuck', "<---_that_is_so_funny_hahahahhahahaha"], brief="Breed")
    async def breed(self, ctx):
        async with self.bot.pool.acquire() as conn:
            children = await conn.fetchval("SELECT COUNT(*) FROM children WHERE lover1_id = $1 OR lover2_id = $1", ctx.author.id)
            marriage = await conn.fetchrow("SELECT user1_id, user2_id FROM marriages WHERE user1_id = $1 OR user2_id = $1", ctx.author.id)
            if marriage is None:
                return await ctx.send("You aren't married", delete_after=30)
            if children >= 5:
                return await ctx.send("You already have 5 children. Are you crazy wanting more?", delete_after=30)

            if marriage['user1_id'] == ctx.author.id:
                user = self.bot.get_user(marriage['user2_id'])
            else:
                user = self.bot.get_user(marriage['user1_id'])


            asking = await ctx.send(f"""{ctx.author.name} would like to breed with {user.name}. {user.name} reply with "I do" for yes and "No" for no.""")
            await self.bot.redis.execute("SET", f"{ctx.author.id}-{ctx.command.qualified_name}", "cooldown", "EX", 3600)
            def check(amsg):
                return amsg.author.id == user.id
            try:
                breed_choice = await self.bot.wait_for('message', timeout=30, check=check)
            except asyncio.TimeoutError:
                await asking.delete()
                await self.bot.redis.execute("DEL", f"{ctx.author.id}-{ctx.command.qualified_name}")
                return await ctx.send(f"{user.name} does not want to make a child with you.")

            if breed_choice.content.lower() == "i do":
                if randint(1,2) == 1:
                    await asking.delete()
                    await ctx.send("You didn't successfully make a child.")
                else:
                    gender = choice(["male", "female"])
                    if gender == "male":
                        await asking.delete()
                        congrats = await ctx.send("Your efforts were successful! He's a male! Please enter the babies name.")
                    else:
                        await asking.delete()
                        congrats = await ctx.send("Your efforts were successful! She's a female! Please enter the babies name.")

                    def check(amsg):
                        return amsg.author.id == ctx.author.id or amsg.author.id == user.id
                    try:
                        baby_name = await self.bot.wait_for('message', timeout=30, check=check)
                    except asyncio.TimeoutError:
                        await asking.delete()
                        await self.bot.redis.execute("DEL", f"{ctx.author.id}-{ctx.command.qualified_name}")
                        return await ctx.send(f"No name was provided in time.", delete_after=30)

                    if len(baby_name.content) < 3 or len(baby_name.content) > 50:
                        await self.bot.redis.execute("DEL", f"{ctx.author.id}-{ctx.command.qualified_name}")
                        return await ctx.send("The name must be more then 3 chars long and can't be longer then 50 chars.", delete_after=30)

                    await self.bot.pool.execute("INSERT INTO children (lover1_id, lover2_id, child_name, age, gender) VALUES ($1, $2, $3, $4, $5)", ctx.author.id, user.id, baby_name.content, 0, gender)
                    await congrats.delete()
                    await ctx.send(f"Great name! Good luck with your newborn {baby_name.content}.".replace('@','@\u200b'))

            if breed_choice.content.lower() == "no":
                await asking.delete()
                await self.bot.redis.execute("DEL", f"{ctx.author.id}-{ctx.command.qualified_name}")
                return await ctx.send(f"{user.name} does not want to have a child.")

            await asking.delete()
            await self.bot.redis.execute("DEL", f"{ctx.author.id}-{ctx.command.qualified_name}")
            await ctx.send("Invalid choice. Did you type it properly?", delete_after=30)

    @commands.command(description='Check your family')
    async def family(self, ctx):
        async with self.bot.pool.acquire() as conn:
            children = await conn.fetch("SELECT * FROM children WHERE lover1_id = $1 OR lover2_id = $1", ctx.author.id)
            marriage = await conn.fetchrow("SELECT user1_id, user2_id, time_married FROM marriages WHERE user1_id = $1 OR user2_id = $1", ctx.author.id)
            if marriage is None:
                return await ctx.send("You aren't married", delete_after=30)

            if marriage['user1_id'] == ctx.author.id:
                user = self.bot.get_user(marriage['user2_id'])
            else:
                user = self.bot.get_user(marriage['user1_id'])

            marriage_time = datetime.now(timezone.utc) - marriage['time_married']
            e = discord.Embed(colour=0x7289da)
            e.set_author(name=f"{user.name} is married to {ctx.author.name}")
            e.set_footer(text=f"Married {marriage['time_married'].strftime('%x on %X')} ({marriage_time.days}d)")
            num = 0
            for i in children:
                e.add_field(name=children[num]['child_name'], value=f"Gender {children[num]['gender']}; Age {children[num]['age']}; Born {children[num]['birthdate'].strftime('%x on %X')}")
                num += 1
            if num == 0:
                e.add_field(name="No children", value=f"{user.name} and {ctx.author.name} have no children.")
            await ctx.send(embed=e)

    @commands.command(description="Bday!", aliases=["bd", "bday"], hidden=True)
    async def birthday(self, ctx):
        async with self.bot.pool.acquire() as conn:
            children = await conn.fetchrow("SELECT child_name, age, gender, last_bd FROM children WHERE lover1_id = $1 OR lover2_id = $1 ORDER BY RANDOM() LIMIT 1", ctx.author.id)
            if children is None:
                return await ctx.send("You have no children.", delete_after=30)
            user_cooldown = await ctx.bot.redis.pttl(f"{ctx.author.id}-{ctx.command.qualified_name}-{children['child_name']}")
            if user_cooldown == -2:
                marriage = await conn.fetchrow("SELECT user1_id, user2_id, time_married FROM marriages WHERE user1_id = $1 OR user2_id = $1", ctx.author.id)
                if marriage is None:
                    return await ctx.send("You aren't married.", delete_after=30)

                await self.bot.redis.execute("SET", f"{ctx.author.id}-{ctx.command.qualified_name}-{children['child_name']}", "cooldown", "EX", 2630000)
                gender = 'He'
                if children['gender'] == 'female':
                    gender = 'She'
                pre_enjy_msg = await ctx.send(f"It's {children['child_name']}'s birthday! {gender} will be turning {children['age'] + 1}")
                enjoyment_lvl = [f"{children['child_name']} loved the birthday party!", f"{children['child_name']} didn't enjoy the party.", f"{children['child_name']} thinks that was the best party ever!",
                                 f"{ctx.author.name} loves uwu"]
                await asyncio.sleep(4)
                enjy = choice(enjoyment_lvl)
                await pre_enjy_msg.delete()
                time = timedelta(seconds=2630000) + datetime.utcnow()
                await conn.execute("UPDATE children SET age = children.age + 1, last_bd = $1 WHERE child_name = $2", time, children['child_name'])
                await ctx.send(enjy)
            else:
                base_time = user_cooldown
                seconds = round(base_time, 2)
                hours, remainder = divmod(int(seconds), 3600)
                minutes, seconds = divmod(remainder, 60)
                await ctx.send(f"{caution} {children['child_name']} already had there birthday within the last month", delete_after=30)


def setup(bot):
    bot.add_cog(marriage(bot))