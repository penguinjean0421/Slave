import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import json
import os
import re

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(base_path, "..", "config.json")
        self.server_configs = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.server_configs = json.load(f)
            except Exception:
                self.server_configs = {}
        else:
            self.server_configs = {}

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.server_configs, f, indent=4, ensure_ascii=False)

    def get_server_data(self, guild):
        gid = str(guild.id)
        # 오너 정보 안전하게 가져오기 (캐싱되지 않았을 경우 대비)
        owner_name = str(guild.owner) if guild.owner else "알 수 없음"
        
        if gid not in self.server_configs:
            self.server_configs[gid] = {
                "server_name": guild.name,
                "owner_id": guild.owner_id,
                "owner_name": owner_name, # 오너 닉네임 추가
                "log_channel_id": None, 
                "command_channel_id": None,
            }
        else:
            # 실시간 정보 동기화
            self.server_configs[gid]["server_name"] = guild.name
            self.server_configs[gid]["owner_name"] = owner_name
            self.server_configs[gid]["owner_id"] = guild.owner_id
        
        self.save_config() # 변경사항 즉시 저장
        return self.server_configs[gid]

    def get_log_channel(self, guild):
        data = self.get_server_data(guild) 
        log_id = data.get("log_channel_id")
        return self.bot.get_channel(log_id) if log_id else guild.system_channel

    async def send_to_log(self, guild, embed):
        log_channel = self.get_log_channel(guild)
        if log_channel and log_channel.permissions_for(guild.me).send_messages:
            if not embed.timestamp:
                embed.timestamp = datetime.now()
            await log_channel.send(embed=embed)

    # --- [로그 리스너: 이름 뒤에 ID 추가] ---

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="📥 멤버 입장", 
            description=f"{member.mention} **{member} (ID: {member.id})** 님이 서버에 입장했습니다.", 
            color=0x00FF00
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"총 멤버: {member.guild.member_count}명")
        await self.send_to_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="📤 멤버 퇴장", 
            description=f"**{member} (ID: {member.id})** 님이 서버를 떠났습니다.", 
            color=0xFF0000
        )
        embed.set_footer(text=f"남은 멤버: {member.guild.member_count}명")
        await self.send_to_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        embed = discord.Embed(title="📝 메시지 수정됨", url=after.jump_url, color=0xFFA500)
        # 작성자 정보에 ID 포함
        embed.set_author(name=f"{before.author} (ID: {before.author.id})", icon_url=before.author.display_avatar.url)
        embed.add_field(name="수정 전", value=f"```{before.content or '내용 없음'}```", inline=False)
        embed.add_field(name="수정 후", value=f"```{after.content or '내용 없음'}```", inline=False)
        await self.send_to_log(before.guild, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild: return
        embed = discord.Embed(
            title="🗑️ 메시지 삭제됨", 
            description=f"작성자: {message.author.mention} **(ID: {message.author.id})**\n채널: {message.channel.mention}\n내용: ```{message.content or '내용 없음'}```", 
            color=0x333333
        )
        await self.send_to_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel: return
        
        user_info = f"{member.mention} **(ID: {member.id})**"
        
        if not before.channel:
            desc = f"🔊 {user_info} 님이 **{after.channel.name}** 입장"
            color = 0x3498DB
        elif not after.channel:
            desc = f"🔇 {user_info} 님이 **{before.channel.name}** 퇴장"
            color = 0x95A5A6
        else:
            desc = f"🔄 {user_info}: **{before.channel.name}** ➡ **{after.channel.name}**"
            color = 0x9B59B6
            
        await self.send_to_log(member.guild, discord.Embed(description=desc, color=color))

    # --- [유틸리티 함수 및 명령어 생략 - 기존과 동일] ---
    def parse_time(self, time_str: str):
        if not time_str: return None
        if time_str.isdigit(): return int(time_str)
        match = re.match(r"(\d+)([smh])", time_str.lower())
        if not match: return None
        amount, unit = int(match.group(1)), match.group(2)
        return amount * {'s': 1, 'm': 60, 'h': 3600}[unit]

    @commands.command(name="set")
    @commands.has_permissions(administrator=True)
    async def set_command(self, ctx, target: str = None, channel: discord.TextChannel = None):
        if not target or target.lower() not in ["log", "bot"]:
            return await ctx.send(f"❓ 사용법: `{ctx.prefix}set log` 또는 `{ctx.prefix}set bot` [#채널]")
        target_channel = channel or ctx.channel
        gid = str(ctx.guild.id)
        self.get_server_data(ctx.guild) # 여기서 오너 정보 등 업데이트됨
        key = "log_channel_id" if target.lower() == "log" else "command_channel_id"
        self.server_configs[gid][key] = target_channel.id
        self.save_config()
        await ctx.send(embed=discord.Embed(title="✅ 설정 완료", description=f"{target_channel.mention} 채널이 **{target}**용으로 설정되었습니다.", color=0x00ff00))

async def setup(bot):
    await bot.add_cog(System(bot))