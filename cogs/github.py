import discord
from discord.ext import commands

class Github(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        self.github_data = {
            "2358006" : { 
                "id" : "2358006",
                "title" : "📂 과제 아카이브",
                "description" : "과제는 여기에 모아뒀어요.",
            },
            "penguinjean0421" : {
                "id" : "penguinjean0421",
                "title" : "📂 penguinjean's Github", 
                "description" : "봇 개발자의 개인 Github"
            }
        }

    async def send_github_embed(self, ctx, name) :
        data = self.github_data[name]
        embed = discord.Embed(
            title = f"{data['title']}",
            description = f"{data['description']}",
            color = 0x2b3137
        )
        embed.add_field(name = "Link", value = f"[바로가기](https://github.com/{data['id']})", inline = False)
        await ctx.send(embed = embed)
    
    @commands.command(name = "2358006", aliases = ["과제", "이삼오팔공공육"])
    async def report_github(self, ctx) :
        await self.send_github_embed(ctx, "2358006")

    @commands.command(name = "penguinjean0421", aliases = ["penguinjean", "펭귄진", "펭귄청바지"])
    async def personal_github(self, ctx) :
        await self.send_github_embed(ctx, "penguinjean0421")

async def setup(bot):
    await bot.add_cog(Github(bot))