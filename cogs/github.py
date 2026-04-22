import discord
from discord.ext import commands
import logging

class Github(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_errors')
        
        self.github_data = {
            "2358006": {
                "title": "📂 과제 아카이브",
                "description": "과제는 여기에 모아뒀어요.",
                "aliases": ["과제", "레포트", "이삼오팔공공육", "2358006"]
            },
            "penguinjean0421": {
                "title": "📂 penguinjean's Github",
                "description": "수업시간에 심심해서 Slave를 탄생 시킨 사람의 깃허브",
                "aliases": ["penguinjean", "jean", "펭귄진", "펭귄청바지"]
            },
        }

    async def send_github_embed(self, ctx: commands.Context, name: str):
        try:
            data = self.github_data[name]

            embed = discord.Embed(
                title=data['title'],
                description=data['description'],
                color=0x2b3137
            )
            embed.add_field(name="👤 GitHub ID", value=f"`{name}`", inline=True)
            embed.add_field(
                name="🔗 Link",
                value=f"[저장소 방문하기](https://github.com/{name})",
                inline=True
            )

            embed.set_thumbnail(
                url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            )
            embed.set_footer(
                text=f"요청자: {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )

            await ctx.send(embed=embed)
        except Exception as e:
            # 임베드 생성 중 발생할 수 있는 에러(데이터 누락 등) 기록
            raise e

    @commands.command(name="github")
    async def github_search(self, ctx: commands.Context, *, search_text: str = None):
        try:
            prefix = ctx.prefix

            if search_text is None:
                embed = discord.Embed(
                    description=(
                        f"❓ **사용법:** `{prefix}github [키워드]`\n"
                        f"예: `{prefix}github 과제` 또는 `{prefix}github 펭귄진`"
                    ),
                    color=0x95A5A6 
                )
                return await ctx.send(embed=embed)

            target_name = None
            clean_text = search_text.lower().replace(" ", "")

            # 데이터 검색 로직
            for key, info in self.github_data.items():
                if clean_text == key.lower() or clean_text in info["aliases"]:
                    target_name = key
                    break

            if target_name:
                await self.send_github_embed(ctx, target_name)
            else:
                embed = discord.Embed(
                    description=f"🔍 '{search_text}'에 해당하는 정보를 찾을 수 없습니다.",
                    color=0xE74C3C
                )
                await ctx.send(embed=embed)
        except Exception as e:
            raise e


async def setup(bot: commands.Bot):
    await bot.add_cog(Github(bot))