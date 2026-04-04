import json
import os
import time
from urllib.parse import quote

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class PUBGStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("PUBG_API_KEY")
        self.base_url = "https://api.pubg.com/shards"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/vnd.api+json"
        }
        self.current_season = None
        self.main_color = 0xF1C40F  # 기본 컬러 설정

        base_path = os.path.dirname(os.path.abspath(__file__))
        self.cache_file = os.path.join(base_path, "..", "tracking.json")

        # 봇 시작 시 시즌 정보 로드
        self.bot.loop.create_task(self.load_current_season())

    async def load_current_season(self):
        """API를 통해 현재 활성화된 시즌 ID를 자동으로 가져옵니다."""
        try:
            async with aiohttp.ClientSession() as session:
                # steam 샤드를 기준으로 시즌 목록 조회
                url = f"{self.base_url}/steam/seasons"
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        seasons = data.get('data', [])
                        for season in seasons:
                            if season['attributes'].get('isCurrentSeason'):
                                self.current_season = season['id']
                                print(f"✅ PUBG 현재 시즌 로드 완료: {self.current_season}")
                                return
                        if seasons:
                            self.current_season = seasons[-1]['id']
                            print(f"⚠️ 현재 시즌 태그를 찾지 못해 마지막 시즌으로 설정: {self.current_season}")
                    else:
                        print(f"❌ 시즌 로드 실패 (Status: {resp.status})")
        except Exception as e:
            print(f"❌ 시즌 정보를 가져오는 중 오류 발생: {e}")

    async def fetch_pubg_data(self, platform, nickname):
        if not self.current_season:
            await self.load_current_season()
            if not self.current_season:
                return {"error": "시즌 정보를 불러올 수 없습니다. 잠시 후 다시 시도해주세요."}
        async with aiohttp.ClientSession() as session:
            # 1. Player ID 조회
            player_url = f"{self.base_url}/{platform}/players?filter[playerNames]={quote(nickname)}"
            async with session.get(player_url, headers=self.headers) as resp:
                if resp.status == 404:
                    return {"error": "플레이어를 찾을 수 없습니다."}
                if resp.status != 200:
                    return {"error": f"API 오류 ({resp.status})"}
                player_json = await resp.json()
                player_id = player_json['data'][0]['id']

            # 2. Season Stats 조회
            stats_url = f"{self.base_url}/{platform}/players/{player_id}/seasons/{self.current_season}"
            async with session.get(stats_url, headers=self.headers) as resp:
                if resp.status != 200:
                    return {"error": "전적 데이터를 가져올 수 없습니다."}
                stats_json = await resp.json()
            modes = stats_json['data']['attributes']['gameModeStats']
            squad = modes.get('squad', {})
            if squad.get('roundsPlayed', 0) == 0:
                return {"error": "이번 시즌 플레이 기록이 없습니다."}
            rounds = squad['roundsPlayed']
            wins = squad['wins']
            kills = squad['kills']
            damage = squad['damageDealt']
            return {
                "nickname": nickname,
                "platform": platform,
                "adr": round(damage / rounds, 1),
                "kd": round(kills / (rounds - wins) if (rounds - wins) > 0 else kills, 2),
                "win_rate": round((wins / rounds) * 100, 1),
                "top10": round((squad['top10s'] / rounds) * 100, 1),
                "rounds": rounds
            }

    @commands.command(name="pubg", aliases=["배그", "ㅂ그"])
    async def pubg_stats(self, ctx, plat_or_nick: str, *, nickname: str = None):
        # 플랫폼 판별
        if plat_or_nick.lower() in ['kakao', 'kakaotv', '카카오']:
            platform = "kakao"
            target_nick = nickname
        else:
            platform = "steam"
            target_nick = f"{plat_or_nick} {nickname if nickname else ''}".strip()
        if not target_nick:
            embed = discord.Embed(
                description="💡 사용법: `!pubg 닉네임` 또는 `!pubg kakao 닉네임`",
                color=0xFFFFFF
            )
            await ctx.send(embed=embed)
            return

        # 캐시 로직
        cache_key = f"{platform}:{target_nick}"
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}
        current_time = time.time()
        footer = ""

        if cache_key in cache and current_time - cache[cache_key]['timestamp'] < 1800:
            data = cache[cache_key]['data']
            footer = "캐시 데이터 사용 중"
        else:
            async with ctx.typing():
                data = await self.fetch_pubg_data(platform, target_nick)
            if not data or "error" in data:
                error_msg = data["error"] if data else "플레이어를 찾을 수 없습니다."
                embed = discord.Embed(description=f"❌ {error_msg}", color=0xE74C3C)
                await ctx.send(embed=embed)
                return
            cache[cache_key] = {"timestamp": current_time, "data": data}
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=4)
            footer = "실시간 데이터 업데이트 완료"

        # 임베드 구성
        embed = discord.Embed(
            title=f"🔫 PUBG 전적: {data['nickname']}",
            color=self.main_color
        )
        embed.add_field(name="플랫폼", value=platform.upper(), inline=True)
        embed.add_field(name="플레이 횟수", value=f"{data['rounds']}회", inline=True)
        embed.add_field(name="평균 딜량 (ADR)", value=f"**{data['adr']}**", inline=True)
        embed.add_field(name="킬데스 (K/D)", value=f"**{data['kd']}**", inline=True)
        embed.add_field(name="승률", value=f"{data['win_rate']}%", inline=True)
        embed.add_field(name="TOP 10", value=f"{data['top10']}%", inline=True)

        # 닥지지(DAK.GG) 링크
        dak_url = f"https://dak.gg/pubg/players/{quote(data['nickname'])}?platform={platform}"
        embed.add_field(
            name="🔗 상세 전적 (DAK.GG)",
            value=f"[클릭하여 이동]({dak_url})",
            inline=False
        )
        embed.set_footer(text=footer)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PUBGStats(bot))