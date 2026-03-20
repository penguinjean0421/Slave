import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import json
import os
import re

class System(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(base_path, "..", "config.json")
        self.server_configs = {}
        self.load_config()

    def load_config(self) :
        if os.path.exists(self.config_file) :
            with open(self.config_file, 'r', encoding = 'utf-8') as f :
                self.server_configs = json.load(f)
        else :
            self.server_configs = {}

    def save_config(self) :
        with open(self.config_file, 'w', encoding = 'utf-8') as f :
            json.dump(self.server_configs, f, indent = 4, ensure_ascii = False)

    def get_server_data(self, guild) :
        gid = str(guild.id)
        if gid not in self.server_configs :
            self.server_configs[gid] = {
                "server_name" : guild.name,
                "owner_name" : guild.owner_name,
                "owner_id" : guild.owner_id,
                "log_channel_name" : None, 
                "log_channel_id" : None, 
                "command_channel_name" : None,
                "command_channel_id" : None,
            }
        else :
            self.server_configs[gid]["server_name"] = guild.name
            self.server_configs[gid]["owner_name"] = guild.owner_name
            self.server_configs[gid]["owner_id"] = guild.owner_id
        return self.server_configs[gid]

    def get_log_channel(self, guild) :
        data = self.get_server_data(guild) 
        log_id = data.get("log_channel_id")
        return self.bot.get_channel(log_id) if log_id else guild.system_channel

    # 로그 채널로 임베드를 보내는 공통 함수
    async def send_to_log(self, guild, embed) :
        log_channel = self.get_log_channel(guild)
        if log_channel and log_channel.permissions_for(guild.me).send_messages :
            # 로그 채널용 임베드에는 언제 발생했는지 타임스탬프 추가
            if not embed.timestamp :
                embed.timestamp = datetime.now()
            await log_channel.send(embed = embed)

    async def cog_check(self, ctx) :
        data = self.get_server_data(ctx.guild)
        cmd_id = data.get("command_channel_id")
        if cmd_id and ctx.channel.id !=  cmd_id :
            return ctx.author.guild_permissions.administrator
        return True
    
    def parse_time(self, time_str : str) :
        if not time_str : return None
        if time_str.isdigit() : return int(time_str)
        match = re.match(r"(\d+)([smh])", time_str.lower())
        if not match : return None
        amount, unit = int(match.group(1)), match.group(2)
        return amount * {'s' : 1, 'm' : 60, 'h' : 3600}[unit]

    # --- 채널 설정 관련 ---
    @commands.command(name = "set")
    @commands.has_permissions(administrator = True)
    async def set_command(self, ctx, target : str = None, channel : discord.TextChannel = None) :
        target = target.lower() if target else None
        target_channel = channel or ctx.channel
        gid = str(ctx.guild.id)
        self.get_server_data(ctx.guild)

        if target in ["log", "bot"] :
            key = "log_channel" if target == "log" else "command_channel"
            self.server_configs[gid][f"{key}_name"] = target_channel.name
            self.server_configs[gid][f"{key}_id"] = target_channel.id
            self.save_config()
            embed = discord.Embed(title = "✅ 설정 완료", description = f"{target_channel.mention} 채널이 **{target}**용으로 설정되었습니다.", color = 0x00ff00)
            await ctx.send(embed = embed)
        else :
            embed = discord.Embed(title = "❓ 사용법", description = f"`{ctx.prefix}set log` 또는 `{ctx.prefix}set bot`", color = 0xEEEEEE)
            await ctx.send(embed = embed)

    # --- 관리 명령어 (로그 연동 포함) ---

    @commands.command(name = "mute", aliases = ["뮤트"])
    @commands.has_permissions(mute_members = True)
    async def server_mute(self, ctx, member : discord.Member = None, time : str = None) :
        if not member : return await ctx.send("❓ 유저를 언급해 주세요.")
        seconds = self.parse_time(time)
        if member.voice :
            await member.edit(mute = True, reason = f"{ctx.author} | {time or '무기한'}")
            embed = discord.Embed(description = f"🔇 {member.mention} 마이크 차단 ({time or '무기한'})", color = 0xe74c3c)
            await ctx.send(embed = embed)
            await self.send_to_log(ctx.guild, embed)
            if seconds :
                await asyncio.sleep(seconds)
                if member.voice :
                    await member.edit(mute = False)
                    await self.send_to_log(ctx.guild, discord.Embed(description = f"🔊 {member.mention} 마이크 해제 (시간 종료)", color = 0x2ecc71))

    @commands.command(name = "deafen", aliases = ["데픈"])
    @commands.has_permissions(deafen_members = True)
    async def server_deafen(self, ctx, member : discord.Member = None, time : str = None) :
        if not member : return await ctx.send("❓ 유저를 언급해 주세요.")
        seconds = self.parse_time(time)
        if member.voice :
            await member.edit(deafen = True, reason = f"{ctx.author} | {time or '무기한'}")
            embed = discord.Embed(description = f"🎧 {member.mention} 헤드셋 차단 ({time or '무기한'})", color = 0x3498DB)
            await ctx.send(embed = embed)
            await self.send_to_log(ctx.guild, embed)
            if seconds :
                await asyncio.sleep(seconds)
                if member.voice :
                    await member.edit(deafen = False)
                    await self.send_to_log(ctx.guild, discord.Embed(description = f"🔊 {member.mention} 헤드셋 해제 (시간 종료)", color = 0x2ECC71))

    @commands.command(name = "timeout", aliases = ["타임아웃"])
    @commands.has_permissions(moderate_members = True)
    async def server_timeout(self, ctx, member : discord.Member = None, time : str = None, *, reason = "사유 없음") :
        seconds = self.parse_time(time)
        if not member or not seconds : return await ctx.send("❓ 유저와 시간을 입력하세요. (ex : 10m)")
        duration = timedelta(seconds = seconds)
        await member.timeout(duration, reason = reason)
        embed = discord.Embed(title = "⏳ 타임아웃", description = f"{member.mention} ({time})", color = 0xffa500)
        embed.add_field(name = "사유", value = reason)
        embed.set_footer(text = f"실행자 : {ctx.author}")
        await ctx.send(embed = embed)
        await self.send_to_log(ctx.guild, embed)

    @commands.command(name = "kick", aliases = ["추방"])
    @commands.has_permissions(kick_members = True)
    async def server_kick(self, ctx, member : discord.Member = None, *, reason = "사유 없음") :
        if not member : return
        await member.kick(reason = reason)
        embed = discord.Embed(title = "👞 추방 완료", description = f"{member.mention} 님이 추방되었습니다.", color = 0xffcc00)
        embed.add_field(name = "사유", value = reason)
        await ctx.send(embed = embed)
        await self.send_to_log(ctx.guild, embed)

    @commands.command(name = "ban", aliases = ["차단"])
    @commands.has_permissions(ban_members = True)
    async def server_ban(self, ctx, member : discord.Member = None, *, reason = "사유 없음") :
        if not member : return
        await member.ban(reason = reason, delete_message_days = 1)
        embed = discord.Embed(title = "🚫 차단 완료", description = f"{member.mention} 님이 차단되었습니다.", color = 0xff0000)
        embed.add_field(name = "사유", value = reason)
        await ctx.send(embed = embed)
        await self.send_to_log(ctx.guild, embed)

    # --- 리스너 (기존과 동일) ---
    @commands.Cog.listener()
    async def on_message_delete(self, message) :
        if message.author.bot : return
        embed = discord.Embed(title = "🗑️ 메시지 삭제", description = f"작성자 : {message.author.mention}\n내용 : ```{message.content}```", color = 0x333333)
        await self.send_to_log(message.guild, embed)

async def setup(bot) :
    await bot.add_cog(System(bot))