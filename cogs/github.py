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
                "color" : 0x2b3137,
                "aliases" : ["과제", "이삼오팔공공육"]
            },
            "penguinjean0421" : {
                "id" : "penguinjean0421",
                "title" : "📂 penguinjean's Github", 
                "description" : "봇 개발자의 개인 Github",
                "color" : 0x0f4c81, 
                "aliases" : ["penguinjean", "펭귄진", "펭귄청바지"]
            }
        }

    async def send_github_embed(self, ctx, name) : 
        data = self.github_data[name]
        embed = discord.Embed(
            title = f"{data['title']}",
            description = f"{data['description']}",
            color = data['color']
        )
        embed.add_field(name = "Link", value = f"[바로가기](https://github.com/{data['id']})", inline = False)
        await ctx.send(embed = embed)

    @commands.command(name = "github", aliases = ["깃허브"])
    async def github_search(self, ctx, *, search_text: str = None):
        if search_text is None:
            return await ctx.send("❓ 사용법: `!github 과제` 또는 `!github 펭귄진`")
        target_name = None
        clean_text = search_text.lower().replace(" ", "")
        for key, info in self.github_data.items() :
            if clean_text == key or clean_text in info["aliases"] :
                target_name = key
                break
        if target_name :
            await self.send_github_embed(ctx, target_name)
        else:
            await ctx.send(f"🔍 '{search_text}'에 해당하는 정보를 찾을 수 없습니다.")

async def setup(bot) :
    await bot.add_cog(Github(bot))