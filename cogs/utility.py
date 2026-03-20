from discord.ext import commands
import random

class Utility(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot

    # 제시된 것중에 하나 선택
    @commands.command(name = "choose")
    async def choose(self, ctx, *options) : 
        if len (options) < 2 :
            await ctx.send("최소 2개이상의 선택지를 제시하십시오")
        else :
            select = random.choice(options)
            await ctx.send(f"{select}")

async def setup(bot) :
    await bot.add_cog(Utility(bot))