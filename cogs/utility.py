import random
import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.menu_list = {
            "한식": ["비빔밥 🥗", "김치찌개 🥘", "삼겹살 🥓", "불고기 🥩", "국밥 🍲", "제육볶음 🍛"],
            "중식": ["짜장면 🍜", "짬뽕 🌶️", "탕수육 🥢", "마라탕 🥘", "볶음밥 🍚", "딤섬 🥟"],
            "일식": ["초밥 🍣", "라멘 🍜", "돈카츠 🍱", "규동 🍚", "우동 🥢", "소바 🧊"],
            "양식": ["파스타 🍝", "피자 🍕", "스테이크 🥩", "햄버거 🍔", "샐러드 🥗", "리조또 🥘"],
            "분식/기타": ["떡볶이 🍡", "치킨 🍗", "샌드위치 🥪", "쌀국수 🍜", "타코 🌮"]
        }

        self.time_data = {
            "아침": ["토스트 🍞", "시리얼 🥣", "요거트 🍦", "과일 🍎", "스크램블 에그 🍳", "누룽지 🍲"],
            "점심": ["김치볶음밥 🍛", "돈까스 🍱", "냉면 🍜", "샌드위치 🥪", "제육덮밥 🍛", "칼국수 🥢"],
            "저녁": ["삼겹살 🥓", "치킨 🍗", "피자 🍕", "스테이크 🥩", "초밥 🍣", "곱창 🥘"],
            "야식": ["라면 🍜", "족발 🐷", "보쌈 🍖", "닭발 🐾", "떡볶이 🍡", "튀김 🍤"]
        }

    @commands.command(name="choose", aliases=["선택", "골라줘"])
    async def choose(self, ctx: commands.Context, *options: str):
        prefix = ctx.prefix
        if len(options) < 2:
            embed = discord.Embed(
                title="❓ 선택지가 부족함",
                description=f"최소 2개 이상의 선택지를 입력합시다.\n예: `{prefix}choose 짜장면 짬뽕 탕수육`",
                color=0xE74C3C
            )
            return await ctx.send(embed=embed)
        select = random.choice(options)
        embed = discord.Embed(
            title="🤔 제 선택은요...",
            description=f"작성하신 **{len(options)}개**의 선택지 중에서 골라봤어요!",
            color=0x3498DB
        )
        embed.add_field(name="📋 후보 목록", value=f"`{'`, `'.join(options)}`", inline=False)
        embed.add_field(name="✨ 최종 결정", value=f"🎉 **{select}**", inline=False)
        embed.set_footer(
            text=f"요청자: {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        await ctx.send(embed=embed)

    @commands.command(name="menu", aliases=["메뉴", "메뉴추천", "뭐먹지", "머먹지"])
    async def recommend_menu(self, ctx: commands.Context, category: str = None):
        prefix = ctx.prefix
        target_list = None
        display_category = ""

        # 카테고리 판별 (시간대별 또는 종류별)
        if category in self.time_data:
            target_list = self.time_data[category]
            display_category = category
        elif category in self.menu_list:
            target_list = self.menu_list[category]
            display_category = category

        # 지정된 카테고리가 없거나 잘못된 경우 전체 메뉴에서 선택
        if not target_list:
            combined_menus = []
            for m in self.menu_list.values():
                combined_menus.extend(m)
            for t in self.time_data.values():
                combined_menus.extend(t)
            target_list = list(set(combined_menus))
            display_category = "전체 메뉴"
        food = random.choice(target_list)
        embed = discord.Embed(
            title="🍴 메뉴 추천 시스템",
            description=f"{ctx.author.mention}님, **{display_category}** 카테고리에서 골라봤어요!",
            color=0xF1C40F
        )
        embed.add_field(name="오늘의 추천", value=f"✨ **{food}**", inline=False)
        embed.set_footer(
            text=f"팁: {prefix}뭐먹지 [아침/점심/한식/중식/일식 등]을 입력해 보세요!"
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))