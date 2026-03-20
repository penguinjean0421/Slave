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
        # 서버장 정보 갱신
        owner_name = str(guild.owner) if guild.owner else "알 수 없음"
        
        if gid not in self.server_configs:
            self.server_configs[gid] = {
                "server_name": guild.name,
                "owner_id": guild.owner_id,
                "owner_name": owner_name,
                "log_channel_id": None, 
                "command_channel_id": None,
            }
        else:
            # 기존 데이터가 있어도 이름이 바뀌었을 수있으니 갱신 ㄱㄱ
            self.server_configs[gid]["server_name"] = guild.name
            self.server_configs[gid]["owner_name"] = owner_name
            self.server_configs[gid]["owner_id"] = guild.owner_id
        self.save_config() # 변경된 정보 저장

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

    async def cog_check(self, ctx):
        if not ctx.guild: return False
        data = self.get_server_data(ctx.guild)
        cmd_id = data.get("command_channel_id")
        if cmd_id and ctx.channel.id != cmd_id:
            return ctx.author.guild_permissions.administrator
        return True
    
    def parse_time(self, time_str: str):
        if not time_str: return None
        if time_str.isdigit(): return int(time_str)
        match = re.match(r"(\d+)([smh])", time_str.lower())
        if not match: return None
        amount, unit = int(match.group(1)), match.group(2)
        return amount * {'s': 1, 'm': 60, 'h': 3600}[unit]

    # --- 채널 설정 ---
    @commands.command(name="set")
    @commands.has_permissions(administrator=True)
    async def set_command(self, ctx, target: str = None, channel: discord.TextChannel = None):
        if not target or target.lower() not in ["log", "bot"]:
            return await ctx.send(f"❓ 사용법: `{ctx.prefix}set log` 또는 `{ctx.prefix}set bot` [#채널]")
        
        target = target.lower()
        target_channel = channel or ctx.channel
        gid = str(ctx.guild.id)
        self.get_server_data(ctx.guild) # 여기서 서버장 정보 갱신됨

        key = "log_channel_id" if target == "log" else "command_channel_id"
        self.server_configs[gid][key] = target_channel.id
        self.save_config()
        await ctx.send(embed=discord.Embed(title="✅ 설정 완료", description=f"{target_channel.mention} 채널이 **{target}**용으로 설정되었습니다.", color=0x00ff00))

    # 로그 출력
    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="📥 멤버 입장", 
            description=f"{member.mention} **{member} (ID: {member.id})** 님이 입장했습니다.", 
            color=0x00FF00
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id} | 총 멤버: {member.guild.member_count}명")
        await self.send_to_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="📤 멤버 퇴장", 
            description=f"**{member} (ID: {member.id})** 님이 서버를 떠났습니다.", 
            color=0xFF0000
        )
        embed.set_footer(text=f"ID: {member.id} | 남은 멤버: {member.guild.member_count}명")
        await self.send_to_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        embed = discord.Embed(title="📝 메시지 수정됨", url=after.jump_url, color=0xFFA500)
        embed.set_author(name=f"{before.author} (ID: {before.author.id})", icon_url=before.author.display_avatar.url)
        embed.add_field(name="수정 전", value=f"```{before.content or '내용 없음'}```", inline=False)
        embed.add_field(name="수정 후", value=f"```{after.content or '내용 없음'}```", inline=False)
        embed.set_footer(text=f"채널: #{before.channel.name}")
        await self.send_to_log(before.guild, embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel: return
        
        user_info = f"{member.mention} **(ID: {member.id})**"
        
        if not before.channel: # 입장
            desc = f"🔊 {user_info} 님이 **{after.channel.name}** 채널 입장"
            color = 0x3498DB
        elif not after.channel: # 퇴장
            desc = f"🔇 {user_info} 님이 **{before.channel.name}** 채널 퇴장"
            color = 0x95A5A6
        else: # 이동
            desc = f"🔄 {user_info}: **{before.channel.name}** ➡ **{after.channel.name}**"
            color = 0x9B59B6
            
        await self.send_to_log(member.guild, discord.Embed(description=desc, color=color))

    # 관리자 명령어
    @commands.command(name="mute", aliases=["뮤트"])
    @commands.has_permissions(mute_members=True)
    async def server_mute(self, ctx, member: discord.Member = None, time: str = None):
        if not member or not member.voice: return await ctx.send("❓ 음성 채널에 있는 유저를 언급해 주세요.")
        seconds = self.parse_time(time)
        await member.edit(mute=True, reason=f"{ctx.author} | {time or '무기한'}")
        
        msg = f"🔇 {member.mention} **(ID: {member.id})** 마이크 차단 ({time or '무기한'})"
        embed = discord.Embed(description=msg, color=0xe74c3c)
        await ctx.send(embed=embed)
        await self.send_to_log(ctx.guild, embed)
        
        if seconds:
            await asyncio.sleep(seconds)
            try: await member.edit(mute=False)
            except: pass

    @commands.command(name="unmute", aliases=["언뮤트", "뮤트해제"])
    @commands.has_permissions(mute_members=True)
    async def server_unmute(self, ctx, member: discord.Member = None):
        if not member or not member.voice:
            return await ctx.send("❓ 음성 채널에 있는 유저를 언급해 주세요.")
        
        await member.edit(mute=False, reason=f"{ctx.author} | 즉시 해제")
        
        msg = f"🔊 {member.mention} **(ID: {member.id})** 마이크 차단 해제"
        embed = discord.Embed(description=msg, color=0x2ECC71) # 해제는 녹색 계열
        await ctx.send(embed=embed)
        await self.send_to_log(ctx.guild, embed)

    @commands.command(name="deafen", aliases=["데픈", "귀막"])
    @commands.has_permissions(deafen_members=True)
    async def server_deafen(self, ctx, member: discord.Member = None, time: str = None):
        if not member or not member.voice: 
            return await ctx.send("❓ 음성 채널에 있는 유저를 언급해 주세요.")
            
        seconds = self.parse_time(time)
        # 서버 데픈 적용
        await member.edit(deafen=True, reason=f"{ctx.author} | {time or '무기한'}")
        
        msg = f"🎧 {member.mention} **(ID: {member.id})** 헤드셋 차단 ({time or '무기한'})"
        embed = discord.Embed(description=msg, color=0x3498DB) # 데픈은 보통 파란색 계열을 사용합니다.
        await ctx.send(embed=embed)
        await self.send_to_log(ctx.guild, embed)
        
        if seconds:
            await asyncio.sleep(seconds)
            try: 
                if member.voice:
                    await member.edit(deafen=False)
                    embed = discord.Embed(description=f"🔊 {member.mention} 헤드셋 차단 해제 (시간 종료)", color=0x2ECC71)
                    await self.send_to_log(ctx.guild, embed)
            except: 
                pass

    @commands.command(name="undeafen", aliases=["언데픈", "귀막해제"])
    @commands.has_permissions(deafen_members=True)
    async def server_undeafen(self, ctx, member: discord.Member = None):
        if not member or not member.voice:
            return await ctx.send("❓ 음성 채널에 있는 유저를 언급해 주세요.")

        await member.edit(deafen=False, reason=f"{ctx.author} | 즉시 해제")
        
        msg = f"🎧 {member.mention} **(ID: {member.id})** 헤드셋 차단 해제"
        embed = discord.Embed(description=msg, color=0x2ECC71)
        await ctx.send(embed=embed)
        await self.send_to_log(ctx.guild, embed)

    @commands.command(name="timeout", aliases=["타임아웃"])
    @commands.has_permissions(moderate_members=True)
    async def server_timeout(self, ctx, member: discord.Member = None, time: str = None, *, reason="사유 없음"):
        seconds = self.parse_time(time)
        if not member or not seconds: return await ctx.send("❓ 유저와 시간(ex: 10m)을 입력하세요.")
        
        await member.timeout(timedelta(seconds=seconds), reason=reason)
        embed = discord.Embed(title="⏳ 타임아웃", description=f"{member.mention} **(ID: {member.id})** ({time})", color=0xffa500)
        embed.add_field(name="사유", value=reason)
        await ctx.send(embed=embed)
        await self.send_to_log(ctx.guild, embed)

    @commands.command(name="kick", aliases=["추방"])
    @commands.has_permissions(kick_members=True)
    async def server_kick(self, ctx, member: discord.Member = None, *, reason="사유 없음"):
        if not member: return
        await member.kick(reason=reason)
        embed = discord.Embed(title="👞 추방 완료", description=f"{member.mention} **(ID: {member.id})** 추방됨", color=0xffcc00)
        await ctx.send(embed=embed)
        await self.send_to_log(ctx.guild, embed)

    @commands.command(name="ban", aliases=["차단"])
    @commands.has_permissions(ban_members=True)
    async def server_ban(self, ctx, member: discord.Member = None, *, reason="사유 없음"):
        if not member: return
        await member.ban(reason=reason, delete_message_seconds=86400)
        embed = discord.Embed(title="🚫 차단 완료", description=f"{member.mention} **(ID: {member.id})** 차단됨", color=0xff0000)
        await ctx.send(embed=embed)
        await self.send_to_log(ctx.guild, embed)

async def setup(bot):
    await bot.add_cog(System(bot))