import discord
from discord.ext import commands, tasks
import aiohttp
import json
import os
import time
import re
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

class LoLStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("RIOT_API_KEY")
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.cache_file = os.path.join(base_path, "..", "tracking.json")

        # 1. 사용자 입력 -> 라이엇 정식 플랫폼 코드 변환 사전
        self.platform_alias = {
            'kr': 'kr', 'jp': 'jp1', 'na': 'na1', 'euw': 'euw1', 'eune': 'eun1',
            'br': 'br1', 'lan': 'la1', 'las': 'la2', 'tr': 'tr1', 'ru': 'ru',
            'oc': 'oc1', 'ph': 'ph2', 'sg': 'sg2', 'th': 'th2', 'vn': 'vn2'
        }

        # 2. 정식 플랫폼 코드 -> 대륙 라우팅 매핑
        self.region_map = {
            'kr': 'asia', 'jp1': 'asia',
            'na1': 'americas', 'br1': 'americas', 'la1': 'americas', 'la2': 'americas',
            'euw1': 'europe', 'eun1': 'europe', 'tr1': 'europe', 'ru': 'europe',
            'oc1': 'sea', 'ph2': 'sea', 'sg2': 'sea', 'th2': 'sea', 'vn2': 'sea'
        }

        if not os.path.exists(self.cache_file):
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

        if not self.clean_cache_task.is_running():
            self.clean_cache_task.start()

    @tasks.loop(minutes=10)
    async def clean_cache_task(self):
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            current_time = time.time()
            new_data = {k: v for k, v in data.items() if current_time - v['timestamp'] < 1800}
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"캐시 정리 중 오류 발생: {e}")

    async def fetch_riot_data(self, platform, name, tag):
        routing = self.region_map.get(platform, 'asia')
        headers = {"X-Riot-Token": self.api_key}
        
        async with aiohttp.ClientSession() as session:
            # Account-V1
            acc_url = f"https://{routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(name)}/{quote(tag)}"
            async with session.get(acc_url, headers=headers) as resp:
                if resp.status != 200: return None
                acc_data = await resp.json()
                puuid = acc_data['puuid']

            # Summoner-V4
            sum_url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            async with session.get(sum_url, headers=headers) as resp:
                if resp.status != 200: return None
                sum_data = await resp.json()
                profile_icon = sum_data.get('profileIconId', 1)
                level = sum_data.get('summonerLevel', 0)

            # League-V4
            league_url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
            async with session.get(league_url, headers=headers) as resp:
                if resp.status != 200: return None
                league_data = await resp.json()

            res = {
                "level": level, "icon": profile_icon,
                "solo": {"tier": "Unranked", "lp": 0, "w": 0, "l": 0},
                "flex": {"tier": "Unranked", "lp": 0, "w": 0, "l": 0},
                "total_w": 0, "total_l": 0
            }

            for entry in league_data:
                q_type = entry['queueType']
                info = {"tier": f"{entry['tier']} {entry['rank']}", "lp": entry['leaguePoints'], "w": entry['wins'], "l": entry['losses']}
                if q_type == 'RANKED_SOLO_5x5': res['solo'] = info
                elif q_type == 'RANKED_FLEX_SR': res['flex'] = info
                res['total_w'] += entry['wins']
                res['total_l'] += entry['losses']
            return res

    @commands.command(name="lol")
    async def lol_stats(self, ctx, region_or_id: str, *, args: str = None):
        """
        사용법 1: !lol 찾았다오마이걸#0421 (기본 KR 서버로 작동)
        사용법 2: !lol na Doublelift#NA1 (해외 서버 지정)
        사용법 3: !lol 찾았다오마이걸#0421 갱신 (강제 업데이트)
        """
        
        # 1. 지역 입력 여부 판단 (첫 번째 인자에 #이 있으면 지역 생략으로 간주)
        if "#" in region_or_id:
            region_input = "kr"  # #이 포함되어 있으므로 기본 KR 서버 설정
            # region_or_id가 닉네임 전체이므로, 뒤에 붙은 args(갱신 등)와 합쳐줍니다.
            riot_id_raw = f"{region_or_id} {args if args else ''}".strip()
        else:
            region_input = region_or_id
            riot_id_raw = args if args else ""

        # 2. 지역 코드 자동 보정 (na -> na1 등)
        platform = self.platform_alias.get(region_input.lower(), region_input.lower())

        # 잘못된 지역명이 들어왔을 때 처리
        if platform not in self.region_map:
            valid_list = ", ".join(self.platform_alias.keys())
            await ctx.send(embed=discord.Embed(
                description=f"❌ 알 수 없는 지역입니다.\n지원: `{valid_list}`", 
                color=0xe74c3c
            ))
            return

        # 3. 갱신 키워드 체크 및 ID 분리
        force_update = "갱신" in riot_id_raw
        riot_id = riot_id_raw.replace("갱신", "").strip()

        # #이 없는 경우 예외 처리
        if "#" not in riot_id:
            await ctx.send(embed=discord.Embed(
                description="💡 예시: `!lol 찾았다오마이걸#0421` 또는 `!lol na Doublelift#NA1`", 
                color=0xf39c12
            ))
            return

        # --- 이후 캐시 확인 및 API 호출 로직 ---
        cache_key = f"{platform}:{riot_id}"
        
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except:
            cache = {}

        current_time = time.time()
        data = None
        footer = ""

        # 캐시 판단 로직
        if not force_update and cache_key in cache and current_time - cache[cache_key]['timestamp'] < 1500:
            data = cache[cache_key]['data']
            footer = "캐시 데이터 사용 중"
        
        if data is None:
            async with ctx.typing():
                try:
                    name, tag = riot_id.rsplit("#", 1)
                    data = await self.fetch_riot_data(platform, name, tag)
                except Exception as e:
                    print(f"오류: {e}")
                    data = None
            
            if not data:
                await ctx.send(embed=discord.Embed(description="❌ 소환사를 찾을 수 없습니다. (이름#태그 확인)", color=0xe74c3c))
                return
            
            # 캐시 저장
            cache[cache_key] = {"timestamp": current_time, "data": data}
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=4)
            footer = "실시간 데이터 업데이트 완료"

        # 4. OP.GG용 주소 생성 및 임베드 출력
        opgg_region = re.sub(r'\d+', '', platform)
        encoded_id = quote(riot_id.replace('#', '-'))
        opgg_url = f"https://www.op.gg/summoners/{opgg_region}/{encoded_id}"

        embed = discord.Embed(title=f"🎮 [{platform.upper()}] {riot_id} (Lv.{data['level']})", color=0x1abc9c)
        embed.set_thumbnail(url=f"https://ddragon.leagueoflegends.com/cdn/14.6.1/img/profileicon/{data['icon']}.png")

        s = data['solo']
        s_wr = round(s['w']/(s['w']+s['l'])*100, 1) if (s['w']+s['l']) > 0 else 0
        embed.add_field(name="🏆 솔로 랭크", value=f"**{s['tier']}**\n{s['lp']} LP\n{s['w']}승 {s['l']}패 ({s_wr}%)", inline=True)

        f = data['flex']
        f_wr = round(f['w']/(f['w']+f['l'])*100, 1) if (f['w']+f['l']) > 0 else 0
        embed.add_field(name="⚔️ 자유 랭크", value=f"**{f['tier']}**\n{f['lp']} LP\n{f['w']}승 {f['l']}패 ({f_wr}%)", inline=True)

        embed.add_field(name="🔗 자세한 전적 (OP.GG)", value=f"[클릭하여 이동]({opgg_url})", inline=False)
        embed.set_footer(text=footer)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LoLStats(bot))