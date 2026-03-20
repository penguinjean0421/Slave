import discord
from discord.ext import commands

class Information(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        # SNS Links
        self.credit_data = {
            "credit" : {
                "developer" : "penguinjean0421",
                "illustrator" : "aram", 
                "supporter" : "girls from gsw",
                "color" : 0x0f4c81, 
            },
        }

    # 크레딧 임베드
    async def send_credit_embed(self, ctx, name) :
        data = self.credit_data[name]
        embed = discord.Embed(
            title = "Thanks for making Slave",
            color = data['color']
            )
        embed.add_field(name = "Developer", value = f"[@{'developer'}](https://www.github.com/{data['developer']})", inline = False)
        embed.add_field(name = "Illustrator", value = f"@{'illustrator'}", inline = False)
        embed.add_field(name = "Supporter", value = f"girls from gsw", inline = False)

        await ctx.send(embed = embed)

    @commands.command(name = "credit", aliases = ["크레딧"])
    async def credit(self, ctx):
        await self.send_credit_embed(ctx, "credit")

async def setup(bot) :
    await bot.add_cog(Information(bot))