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
            # 경고/오류 표준 색상 (Alizarin)
            embed = discord.Embed(
                title="❓ 선택지가 부족함",
                description=f"최소 2개 이상의 선택지를 입력합시다.\n예: `{prefix}choose 짜장면 짬뽕 탕수육`",
                color=0xE74C3C
            )
            return await ctx.send(embed=embed)
            
        select = random.choice(options)
        # 성공/결과 알림 (Emerald)
        embed = discord.Embed(
            title="🤔 제 선택은요...",
            description=f"작성하신 **{len(options)}개**의 선택지 중에서 골라봤어요!",
            color=0x2ECC71
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

        if category in self.time_data:
            target_list = self.time_data[category]
            display_category = category
        elif category in self.menu_list:
            target_list = self.menu_list[category]
            display_category = category

        if not target_list:
            combined_menus = []
            for m in self.menu_list.values():
                combined_menus.extend(m)
            for t in self.time_data.values():
                combined_menus.extend(t)
            target_list = list(set(combined_menus))
            display_category = "전체 메뉴"
            
        food = random.choice(target_list)
        # 서비스 아이덴티티 색상 (Flat Yellow)
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

    @commands.command(name="kill")
    async def kill_reason(self, ctx, member: discord.Member = None):
        monsters = ["교수", "과제", "시험"]

        death_messages = [
        "높은 곳에서 떨어졌습니다.",
        "바닥에 너무 세게 부딪혔습니다.",
        "용암에 빠졌습니다.",
        "불타버렸습니다.",
        "선인장에 찔려 죽었습니다.",
        "물속에서 숨이 막혔습니다.",
        "벽 속에서 압사당했습니다.",
        "번개에 맞았습니다.",
        "마법으로 살해당했습니다.",
        "폭발에 휘말렸습니다.",
        "얼어 죽었습니다.",
        "겉날개를 타던 중 벽에 부딪혔습니다.",
        "너무 배가 고파서 죽었습니다.",
        "자신의 포션에 독살당했습니다.",
        "{attacker}에게 살해당했습니다.",
        "{attacker}에게 저격당했습니다.",
        "{attacker}에 의해 운명을 달리했습니다.",
        "{attacker}이(가) 쏜 화살에 맞았습니다.",
        "{attacker}와(과) 싸우다 너무 높이 올라갔습니다.",
        "{attacker}와(과) 싸우던 중 용암에 빠졌습니다.",
        "{attacker}에게 밀려 선인장에 찔려 죽었습니다.",
        "{attacker}에 의해 불타버렸습니다.",
        "{attacker}에게 쫓기다 구석에 몰려 압사당했습니다.",
        "{attacker}와(과) 교전 중 폭발에 휘말렸습니다.",
        "{attacker}이(가) 던진 삼차창에 꿰뚫렸습니다.",
        "{attacker}이(가) 던진 포션에 의해 독살당했습니다.",
        "{attacker}의 협박으로 사망하셨습니다."
        ]

        target = member if member else ctx.author
        chosen_msg = random.choice(death_messages)

        if "{attacker}" in chosen_msg:
            embed_color = 0xff0000

            if member is None or member == ctx.author:
                attacker_name = f"**{random.choice(monsters)}**"
            else:
                attacker_name = f"**{ctx.author.display_name}**"

            full_message = chosen_msg.format(attacker=attacker_name)
        else:
            embed_color=0x36393F
            full_message = chosen_msg

        embed=discord.Embed(
            description=f"**{target.display_name}**이(가) {full_message}",
            color=embed_color
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))