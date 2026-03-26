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
        owner_name = str(guild.owner) if guild.owner else "알 수 없음"
        
        if gid not in self.server_configs:
            self.server_configs[gid] = {
                "server_name": guild.name,
                "owner_id": guild.owner_id,
                "owner_name": owner_name,
                "log_channel_id": None, 
                "punish_log_channel_id": None,
                "command_channel_id": None,
            }
        else:
            self.server_configs[gid]["server_name"] = guild.name
            self.server_configs[gid]["owner_name"] = owner_name
            self.server_configs[gid]["owner_id"] = guild.owner_id
        
        self.save_config()
        return self.server_configs[gid]

    def get_log_channel(self, guild):
        data = self.get_server_data(guild) 
        log_id = data.get("log_channel_id")
        return self.bot.get_channel(log_id) if log_id else guild.system_channel

    def get_punish_channel(self, guild):
        data = self.get_server_data(guild) 
        p_id = data.get("punish_log_channel_id") or data.get("log_channel_id")
        return self.bot.get_channel(p_id) if p_id else guild.system_channel

    async def send_to_log(self, guild, embed):
        log_channel = self.get_log_channel(guild)
        if log_channel and log_channel.permissions_for(guild.me).send_messages:
            if not embed.timestamp:
                embed.timestamp = datetime.now()
            await log_channel.send(embed=embed)

    async def send_punish_log(self, guild, embed):
        log_channel = self.get_punish_channel(guild)
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
        match = re.match(r"(\d+)([smhd])", time_str.lower())
        if not match: return None
        amount, unit = int(match.group(1)), match.group(2)
        return amount * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.guild and ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.message.delete()

    # --- 이벤트 리스너 (일반 로그) ---

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(title="📥 멤버 입장", description=f"{member.mention} **{member}** 님이 입장했습니다.", color=0x2ECC71)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id} | 총 멤버: {member.guild.member_count}명")
        await self.send_to_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(title="📤 멤버 퇴장", description=f"**{member}** 님이 서버를 떠났습니다.", color=0xE74C3C)
        embed.set_footer(text=f"ID: {member.id} | 남은 멤버: {member.guild.member_count}명")
        await self.send_to_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        embed = discord.Embed(title="📝 메시지 수정됨", url=after.jump_url, color=0xF39C12)
        embed.set_author(name=f"{before.author}", icon_url=before.author.display_avatar.url)
        embed.add_field(name="수정 전", value=f"```{before.content or '내용 없음'}```", inline=False)
        embed.add_field(name="수정 후", value=f"```{after.content or '내용 없음'}```", inline=False)
        await self.send_to_log(before.guild, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild: return
        embed = discord.Embed(title="🗑️ 메시지 삭제됨", color=0x34495E)
        embed.description = f"**작성자:** {message.author.mention}\n**채널:** {message.channel.mention}\n**내용:** ```{message.content or '내용 없음'}```"
        await self.send_to_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel: return
        user_info = f"{member.mention} **({member.id})**"
        if not before.channel:
            desc, color = f"🔊 {user_info} 님이 **{after.channel.name}** 입장", 0x3498DB
        elif not after.channel:
            desc, color = f"🔇 {user_info} 님이 **{before.channel.name}** 퇴장", 0x95A5A6
        else:
            desc, color = f"🔄 {user_info}: **{before.channel.name}** ➡ **{after.channel.name}**", 0x9B59B6
        await self.send_to_log(member.guild, discord.Embed(description=desc, color=color))

    # --- 설정 명령어 ---

    @commands.command(name="set")
    @commands.has_permissions(administrator=True)
    async def set_command(self, ctx, target: str = None, channel: discord.TextChannel = None):
        key_map = {"log": "log_channel_id", "bot": "command_channel_id", "punish": "punish_log_channel_id"}
        
        if not target or target.lower() not in key_map:
            embed = discord.Embed(description=f"❓ 사용법: `{ctx.prefix}set [log/punish/bot] [#채널]`", color=0x95A5A6)
            return await ctx.send(embed=embed)
        
        target = target.lower()
        target_channel = channel or ctx.channel
        gid = str(ctx.guild.id)
        
        self.get_server_data(ctx.guild)
        self.server_configs[gid][key_map[target]] = target_channel.id
        self.save_config()

        embed = discord.Embed(description=f"✅ **{target.upper()}** 채널이 {target_channel.mention}로 설정되었습니다.", color=0x3498DB)
        await ctx.send(embed=embed)

    @commands.command(name="reset", aliases=["초기화"])
    @commands.has_permissions(administrator=True)
    async def reset_command(self, ctx, target: str = None):
        gid = str(ctx.guild.id)
        key_map = {"log": "log_channel_id", "bot": "command_channel_id", "punish": "punish_log_channel_id"}
        
        if target == "all":
            self.server_configs.pop(gid, None)
            embed = discord.Embed(description="✅ 모든 설정이 초기화되었습니다.", color=0xE67E22)
        elif target in key_map:
            self.server_configs[gid][key_map[target]] = None
            embed = discord.Embed(description=f"✅ **{target.upper()}** 채널 설정이 해제되었습니다.", color=0x95A5A6)
        else:
            embed = discord.Embed(description=f"❓ 사용법: `{ctx.prefix}reset [log/punish/bot/all]`", color=0x95A5A6)
    
        self.save_config()
        await ctx.send(embed=embed)

    # --- 제제 명령어 --- 

    @commands.command(name="mute", aliases=["뮤트"])
    @commands.has_permissions(administrator=True)
    async def server_mute(self, ctx, member: discord.Member = None, time: str = None):
        if not member or not member.voice: 
            embed = discord.Embed(description="❌ 대상을 찾을 수 없거나 음성 채널에 없습니다.", color=0xE74C3C)
            return await ctx.send(embed=embed)
            
        seconds = self.parse_time(time)
        await member.edit(mute=True, reason=f"실행자: {ctx.author} ({time or '무기한'})")
        
        embed = discord.Embed(description=f"🔇 {member.mention} 마이크 차단 ({time or '무기한'})", color=0xE74C3C)
        await ctx.send(embed=embed)
        await self.send_punish_log(ctx.guild, embed)
        
        if seconds:
            await asyncio.sleep(seconds)
            if member.voice:
                await member.edit(mute=False)
                await self.send_punish_log(ctx.guild, discord.Embed(description=f"🔊 {member.mention} 뮤트 해제 (시간 종료)", color=0x2ECC71))

    @commands.command(name="unmute", aliases=["뮤트해제"])
    @commands.has_permissions(administrator=True)
    async def server_unmute(self, ctx, member: discord.Member = None):
        if not member or not member.voice: 
            embed = discord.Embed(description="❌ 대상이 음성 채널에 없습니다.", color=0xE74C3C)
            return await ctx.send(embed=embed)
            
        await member.edit(mute=False)
        embed = discord.Embed(description=f"🔊 {member.mention} 마이크 차단 해제", color=0x2ECC71)
        await ctx.send(embed=embed)
        await self.send_punish_log(ctx.guild, embed)

    @commands.command(name="vckick", aliases=["음성강퇴"])
    @commands.has_permissions(administrator=True)    
    async def server_vckick(self, ctx, member: discord.Member = None, *, reason="사유 없음"):
        if not member or not member.voice: 
            embed = discord.Embed(description="❌ 대상이 음성 채널에 없습니다.", color=0xE74C3C)
            return await ctx.send(embed=embed)
            
        await member.move_to(None, reason=f"실행자: {ctx.author}")
        embed = discord.Embed(title="👟 음성 강제 퇴장", description=f"{member.mention} 퇴장됨\n사유: {reason}", color=0xF1C40F)
        await ctx.send(embed=embed)
        await self.send_punish_log(ctx.guild, embed)

    @commands.command(name="timeout", aliases=["타임아웃"])
    @commands.has_permissions(administrator=True)    
    async def server_timeout(self, ctx, member: discord.Member = None, time: str = None, *, reason="사유 없음"):
        seconds = self.parse_time(time)
        
        if not member or not seconds: 
            embed = discord.Embed(description=f"❓ 사용법: `{ctx.prefix}timeout @유저 [시간] [사유]`\n예: `{ctx.prefix}timeout @유저 10m 도배`", color=0x95A5A6)
            return await ctx.send(embed=embed)
            
        try:
            await member.timeout(timedelta(seconds=seconds), reason=f"실행자: {ctx.author} | {reason}")
            embed = discord.Embed(title="⏳ 타임아웃", description=f"{member.mention} ({time})\n사유: {reason}", color=0xF39C12)
            await ctx.send(embed=embed)
            await self.send_punish_log(ctx.guild, embed)
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"❌ 오류: {e}", color=0xE74C3C))

    @commands.command(name="untimeout", aliases=["타임아웃해제", "언타임아웃"])
    @commands.has_permissions(administrator=True)    
    async def server_untimeout(self, ctx, member: discord.Member = None, *, reason="관리자에 의한 해제"):
        if not member: 
            embed = discord.Embed(description=f"❓ 사용법: `{ctx.prefix}untimeout @유저`", color=0x95A5A6)
            return await ctx.send(embed=embed)
            
        if not member.timed_out_until:
            embed = discord.Embed(description=f"❌ {member.mention} 님은 현재 타임아웃 상태가 아닙니다.", color=0xE74C3C)
            return await ctx.send(embed=embed)
            
        try:
            await member.timeout(None, reason=f"실행자: {ctx.author} | {reason}")
            embed = discord.Embed(title="✅ 타임아웃 해제", description=f"{member.mention} 님의 타임아웃이 해제되었습니다.", color=0x2ECC71)
            await ctx.send(embed=embed)
            await self.send_punish_log(ctx.guild, embed)
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"❌ 오류 발생: {e}", color=0xE74C3C))

    @commands.command(name="kick", aliases=["추방"])
    @commands.has_permissions(kick_members=True)
    async def server_kick(self, ctx, member: discord.Member = None, *, reason="사유 없음"):
        if not member: return
        await member.kick(reason=f"실행자: {ctx.author} | {reason}")
        embed = discord.Embed(title="👞 추방 완료", description=f"{member.mention} 추방됨\n사유: {reason}", color=0xE67E22)
        await ctx.send(embed=embed)
        await self.send_punish_log(ctx.guild, embed)

    @commands.command(name="ban", aliases=["차단"])
    @commands.has_permissions(ban_members=True)
    async def server_ban(self, ctx, member: discord.Member = None, *, reason="사유 없음"):
        if not member: 
            embed = discord.Embed(description=f"❓ 사용법: `{ctx.prefix}ban [유저멘션/ID] [사유]`", color=0x95A5A6)
            return await ctx.send(embed=embed)
            
        await member.ban(reason=f"실행자: {ctx.author} | {reason}", delete_message_seconds=86400)
        embed = discord.Embed(title="🚫 차단 완료", description=f"{member.mention} 차단됨\n사유: {reason}", color=0xC0392B)
        await ctx.send(embed=embed)
        await self.send_punish_log(ctx.guild, embed)

    @commands.command(name="unban", aliases=["차단해제"])
    @commands.has_permissions(ban_members=True)
    async def server_unban(self, ctx, *, user_spec: str = None):
        if not user_spec: 
            embed = discord.Embed(description=f"❓ 사용법: `{ctx.prefix}unban [이름#태그] 또는 [ID]`", color=0x95A5A6)
            return await ctx.send(embed=embed) 
            
        async for entry in ctx.guild.bans():
            if user_spec in [str(entry.user.id), str(entry.user)]:
                await ctx.guild.unban(entry.user)
                embed = discord.Embed(title="✅ 차단 해제", description=f"{entry.user} 해제됨", color=0x2ECC71)
                await ctx.send(embed=embed)
                return await self.send_punish_log(ctx.guild, embed)
                
        await ctx.send(embed=discord.Embed(description="❌ 차단 목록에서 찾을 수 없습니다.", color=0xE74C3C))

async def setup(bot):
    await bot.add_cog(System(bot))