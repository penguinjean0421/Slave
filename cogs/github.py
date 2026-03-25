import discord
from discord.ext import commands

class Github(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        self.github_data = {
            "2358006" : { 
                "title" : "📂 과제 아카이브",
                "description" : "과제는 여기에 모아뒀어요.",
                "color" : 0x2b3137,
                "aliases" : ["과제", "레포트", "이삼오팔공공육", "2358006"]
            },
            "penguinjean0421" : {
                "title" : "📂 penguinjean's Github", 
                "description" : "수업시간에 심심해서 Slave를 탄생 시킨 사람의 깃허브",
                "color" : 0x0f4c81, 
                "aliases" : ["penguinjean", "jean", "펭귄진", "펭귄청바지"]
            },
        }

    async def send_github(self, ctx, name) : 
        data = self.github_data[name]
        embed = discord.Embed(
            title = f"{data['title']}",
            description = f"{data['description']}",
            color = data['color']
        )
        embed.add_field(name="👤 GitHub ID", value=f"`{name}`", inline=False)
        embed.add_field(name="🔗 Link", value=f"[저장소 방문하기](https://github.com/{name})", inline=False)
        await ctx.send(embed = embed)

    @commands.command(name = "github", aliases = ["깃허브"])
    async def github_search(self, ctx, *, search_text: str = None):
        if search_text is None:
            return await ctx.send("❓ 사용법: `!github 2358006` or `!github 펭귄진`")
        target_name = None
        clean_text = search_text.lower().replace(" ", "")
        for key, info in self.github_data.items() :
            if clean_text == key or clean_text in info["aliases"] :
                target_name = key
                break
        if target_name :
            await self.send_github(ctx, target_name)
        else:
            await ctx.send(f"🔍 '{search_text}'에 해당하는 정보를 찾을 수 없습니다.")

async def setup(bot) :
    await bot.add_cog(Github(bot))