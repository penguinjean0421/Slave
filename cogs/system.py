import asyncio
import json
import os
import re
from datetime import datetime, timedelta

import discord
from discord.ext import commands


class System(commands.Cog):
    """
    서버 설정 관리 및 로그 시스템을 담당하는 메인 Cog입니다.
    """

    def __init__(self, bot):
        self.bot = bot
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(base_path, "..", "config.json")
        self.server_configs = {}
        self.load_config()

    def load_config(self):
        """설정 파일(JSON)을 로드합니다."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.server_configs = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.server_configs = {}
        else:
            self.server_configs = {}

    def save_config(self):
        """현재 설정을 파일에 저장합니다."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.server_configs, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {e}")

    def get_server_data(self, guild):
        """서버별 데이터 구조를 반환하며, 없을 경우 초기화합니다."""
        gid = str(guild.id)

        if gid not in self.server_configs:
            self.server_configs[gid] = {
                "server_name": guild.name,
                "owner_id": guild.owner_id,
                "owner_name": str(guild.owner),
                "log_channel_id": None,
                "punish_log_channel_id": None,
                "command_channel_id": None,
                "ticket_panel_channel_id": None,
                "ticket_panel_msg_id": None,
                "ticket_count": 0
            }
        else:
            # 필수 키 누락 대비 기본값 채워넣기
            keys = ["ticket_panel_channel_id", "ticket_panel_msg_id", "ticket_count"]
            for key in keys:
                if key not in self.server_configs[gid]:
                    self.server_configs[gid][key] = 0 if "count" in key else None
            self.server_configs[gid]["server_name"] = guild.name

        self.save_config()
        return self.server_configs[gid]

    def get_log_channel(self, guild):
        """설정된 로그 채널을 반환합니다."""
        data = self.get_server_data(guild)
        log_id = data.get("log_channel_id")
        return self.bot.get_channel(log_id) if log_id else guild.system_channel

    def get_punish_channel(self, guild):
        """설정된 처벌 로그 채널을 반환합니다."""
        data = self.get_server_data(guild)
        p_id = data.get("punish_log_channel_id") or data.get("log_channel_id")
        return self.bot.get_channel(p_id) if p_id else guild.system_channel

    async def send_to_log(self, guild, embed):
        """일반 로그 채널에 메시지를 전송합니다."""
        log_channel = self.get_log_channel(guild)
        if log_channel and log_channel.permissions_for(guild.me).send_messages:
            if not embed.timestamp:
                embed.timestamp = datetime.now()
            await log_channel.send(embed=embed)

    async def send_punish_log(self, guild, embed):
        """처벌 로그 채널에 메시지를 전송합니다."""
        log_channel = self.get_punish_channel(guild)
        if log_channel and log_channel.permissions_for(guild.me).send_messages:
            if not embed.timestamp:
                embed.timestamp = datetime.now()
            await log_channel.send(embed=embed)

    async def cog_check(self, ctx):
        """명령어 실행 전 채널 및 권한을 확인합니다."""
        if not ctx.guild:
            return False
        data = self.get_server_data(ctx.guild)
        cmd_id = data.get("command_channel_id")
        if cmd_id and ctx.channel.id != cmd_id:
            return ctx.author.guild_permissions.administrator
        return True

    def parse_time(self, time_str: str):
        """시간 문자열(s, m, h, d)을 초 단위 정수로 변환합니다."""
        if not time_str:
            return None
        if time_str.isdigit():
            return int(time_str)
        match = re.match(r"(\d+)([smhd])", time_str.lower())
        if not match:
            return None
        amount, unit = int(match.group(1)), match.group(2)
        unit_map = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        return amount * unit_map[unit]

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """명령어 성공 시 메시지를 자동 삭제합니다."""
        if ctx.guild and ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.message.delete()

    # --- 이벤트 리스너 (일반 로그) ---

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="📥 멤버 입장",
            description=f"{member.mention} **{member}** 님이 입장했습니다.",
            color=0x2ECC71
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id} | 총 멤버: {member.guild.member_count}명")
        await self.send_to_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="📤 멤버 퇴장",
            description=f"**{member}** 님이 서버를 떠났습니다.",
            color=0xE74C3C
        )
        embed.set_footer(text=f"ID: {member.id} | 남은 멤버: {member.guild.member_count}명")
        await self.send_to_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        embed = discord.Embed(title="📝 메시지 수정됨", url=after.jump_url, color=0xF39C12)
        embed.set_author(name=f"{before.author}", icon_url=before.author.display_avatar.url)
        embed.add_field(name="수정 전", value=f"```{before.content or '내용 없음'}```", inline=False)
        embed.add_field(name="수정 후", value=f"```{after.content or '내용 없음'}```", inline=False)
        await self.send_to_log(before.guild, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return
        embed = discord.Embed(title="🗑️ 메시지 삭제됨", color=0x34495E)
        embed.description = (
            f"**작성자:** {message.author.mention}\n"
            f"**채널:** {message.channel.mention}\n"
            f"**내용:** ```{message.content or '내용 없음'}```"
        )
        await self.send_to_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel:
            return
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
        """서버의 각종 로그 및 티켓 채널을 설정합니다."""
        key_map = {
            "log": "log_channel_id",
            "bot": "command_channel_id",
            "punish": "punish_log_channel_id",
            "ticket": "ticket_panel_channel_id"
        }

        if not target or target.lower() not in key_map:
            embed = discord.Embed(
                description=f"❓ 사용법: `{ctx.prefix}set [log/punish/bot/ticket] [#채널]`",
                color=0x95A5A6
            )
            return await ctx.send(embed=embed)

        target = target.lower()
        target_channel = channel or ctx.channel
        gid = str(ctx.guild.id)
        self.get_server_data(ctx.guild)

        self.server_configs[gid][key_map[target]] = target_channel.id
        embed = discord.Embed(
            description=f"✅ **{target.upper()}** 채널이 {target_channel.mention}로 설정되었습니다.",
            color=0x3498DB
        )

        if target == "ticket":
            ticket_cog = self.bot.get_cog('Ticket')
            if ticket_cog:
                panel_msg = await ticket_cog.send_ticket_panel(target_channel)
                if panel_msg:
                    self.server_configs[gid]["ticket_panel_channel_id"] = target_channel.id
                    self.server_configs[gid]["ticket_panel_msg_id"] = panel_msg.id
                    embed = discord.Embed(
                        description=f"✅ 티켓 패널이 {target_channel.mention}에 생성되었습니다.\n(ID: {panel_msg.id})",
                        color=0x3498DB
                    )
                else:
                    embed = discord.Embed(description="❌ 티켓 메시지 생성에 실패했습니다.", color=0xE74C3C)
                    return await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description="❌ Ticket Cog가 로드되지 않았습니다.", color=0xE74C3C)
                return await ctx.send(embed=embed)

        self.save_config()
        await ctx.send(embed=embed)

    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_command(self, ctx, target: str = None):
        """서버 설정을 초기화하거나 특정 채널 설정을 제거합니다."""
        gid = str(ctx.guild.id)
        key_map = {
            "log": "log_channel_id",
            "bot": "command_channel_id",
            "punish": "punish_log_channel_id",
            "ticket": "ticket_panel_channel_id"
        }

        if target == "all":
            await self.delete_ticket_panel(ctx.guild)
            self.server_configs.pop(gid, None)
            embed = discord.Embed(description="✅ 모든 설정이 초기화되었습니다.", color=0xE67E22)
        elif target and target.lower() in key_map:
            target = target.lower()
            if target == "ticket":
                await self.delete_ticket_panel(ctx.guild)

            if gid in self.server_configs:
                self.server_configs[gid][key_map[target]] = None
                if target == "ticket":
                    self.server_configs[gid]["ticket_panel_msg_id"] = None
                embed = discord.Embed(
                    description=f"✅ **{target.upper()}** 설정 및 패널이 제거되었습니다.",
                    color=0x95A5A6
                )
            else:
                embed = discord.Embed(description="❌ 설정된 데이터가 없습니다.", color=0xE74C3C)
        else:
            embed = discord.Embed(
                description=f"❓ 사용법: `{ctx.prefix}reset [log/punish/bot/ticket/all]`",
                color=0x95A5A6
            )

        self.save_config()
        await ctx.send(embed=embed)

    async def delete_ticket_panel(self, guild):
        """저장된 티켓 패널 메시지를 물리적으로 삭제합니다."""
        gid = str(guild.id)
        config = self.server_configs.get(gid)
        if not config:
            return

        msg_id = config.get("ticket_panel_msg_id")
        chn_id = config.get("ticket_panel_channel_id")

        if msg_id and chn_id:
            channel = self.bot.get_channel(chn_id)
            if not channel:
                try:
                    channel = await self.bot.fetch_channel(chn_id)
                except Exception:
                    return

            try:
                msg = await channel.fetch_message(msg_id)
                await msg.delete()
            except discord.NotFound:
                pass
            except Exception as e:
                print(f"패널 삭제 오류: {e}")

    # --- 처벌(Sanction) 명령어 ---

    @commands.command(name="mute")
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
                unmute_embed = discord.Embed(
                    description=f"🔊 {member.mention} 뮤트 해제 (시간 종료)",
                    color=0x2ECC71
                )
                await self.send_punish_log(ctx.guild, unmute_embed)

    @commands.command(name="unmute")
    @commands.has_permissions(administrator=True)
    async def server_unmute(self, ctx, member: discord.Member = None):
        if not member or not member.voice:
            embed = discord.Embed(description="❌ 대상이 음성 채널에 없습니다.", color=0xE74C3C)
            return await ctx.send(embed=embed)

        await member.edit(mute=False)
        embed = discord.Embed(description=f"🔊 {member.mention} 마이크 차단 해제", color=0x2ECC71)
        await ctx.send(embed=embed)
        await self.send_punish_log(ctx.guild, embed)

    @commands.command(name="deafen")
    @commands.has_permissions(administrator=True)
    async def server_deafen(self, ctx, member: discord.Member = None, time: str = None):
        if not member or not member.voice:
            embed = discord.Embed(description="❌ 대상을 찾을 수 없거나 음성 채널에 없습니다.", color=0xE74C3C)
            return await ctx.send(embed=embed)

        seconds = self.parse_time(time)
        await member.edit(deafen=True, reason=f"실행자: {ctx.author} ({time or '무기한'})")

        embed = discord.Embed(description=f"🔇 {member.mention} 헤드셋 차단 ({time or '무기한'})", color=0xE74C3C)
        await ctx.send(embed=embed)
        await self.send_punish_log(ctx.guild, embed)

        if seconds:
            await asyncio.sleep(seconds)
            if member.voice:
                await member.edit(deafen=False)
                log_embed = discord.Embed(
                    description=f"🔊 {member.mention} 헤드셋 차단 해제 (시간 종료)",
                    color=0x2ECC71
                )
                await self.send_punish_log(ctx.guild, log_embed)

    @commands.command(name="undeafen")
    @commands.has_permissions(administrator=True)
    async def server_undeafen(self, ctx, member: discord.Member = None):
        if not member or not member.voice:
            embed = discord.Embed(description="❌ 대상이 음성 채널에 없습니다.", color=0xE74C3C)
            return await ctx.send(embed=embed)

        await member.edit(deafen=False)
        embed = discord.Embed(description=f"🔊 {member.mention} 헤드셋 차단 해제", color=0x2ECC71)
        await ctx.send(embed=embed)
        await self.send_punish_log(ctx.guild, embed)

    @commands.command(name="vckick")
    @commands.has_permissions(administrator=True)
    async def server_vckick(self, ctx, member: discord.Member = None, *, reason="사유 없음"):
        if not member or not member.voice:
            embed = discord.Embed(description="❌ 대상이 음성 채널에 없습니다.", color=0xE74C3C)
            return await ctx.send(embed=embed)

        await member.move_to(None, reason=f"실행자: {ctx.author}")
        embed = discord.Embed(
            title="👟 음성 강제 퇴장",
            description=f"{member.mention} 퇴장됨\n사유: {reason}",
            color=0xF1C40F
        )
        await ctx.send(embed=embed)
        await self.send_punish_log(ctx.guild, embed)

    @commands.command(name="timeout")
    @commands.has_permissions(administrator=True)
    async def server_timeout(self, ctx, member: discord.Member = None, time: str = None, *, reason="사유 없음"):
        seconds = self.parse_time(time)
        if not member or not seconds:
            embed = discord.Embed(
                description=f"❓ 사용법: `{ctx.prefix}timeout @유저 [시간] [사유]`\n"
                            f"예: `{ctx.prefix}timeout @유저 10m 도배`",
                color=0x95A5A6
            )
            return await ctx.send(embed=embed)

        try:
            await member.timeout(timedelta(seconds=seconds), reason=f"실행자: {ctx.author} | {reason}")
            embed = discord.Embed(
                title="⏳ 타임아웃",
                description=f"{member.mention} ({time})\n사유: {reason}",
                color=0xF39C12
            )
            await ctx.send(embed=embed)
            await self.send_punish_log(ctx.guild, embed)
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"❌ 오류: {e}", color=0xE74C3C))

    @commands.command(name="untimeout")
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
            embed = discord.Embed(
                title="✅ 타임아웃 해제",
                description=f"{member.mention} 님의 타임아웃이 해제되었습니다.",
                color=0x2ECC71
            )
            await ctx.send(embed=embed)
            await self.send_punish_log(ctx.guild, embed)
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"❌ 오류 발생: {e}", color=0xE74C3C))

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def server_kick(self, ctx, member: discord.Member = None, *, reason="사유 없음"):
        if not member:
            return
        await member.kick(reason=f"실행자: {ctx.author} | {reason}")
        embed = discord.Embed(title="👞 추방 완료", description=f"{member.mention} 추방됨\n사유: {reason}", color=0xE67E22)
        await ctx.send(embed=embed)
        await self.send_punish_log(ctx.guild, embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def server_ban(self, ctx, member: discord.Member = None, *, reason="사유 없음"):
        if not member:
            embed = discord.Embed(description=f"❓ 사용법: `{ctx.prefix}ban [유저멘션/ID] [사유]`", color=0x95A5A6)
            return await ctx.send(embed=embed)

        await member.ban(reason=f"실행자: {ctx.author} | {reason}", delete_message_seconds=86400)
        embed = discord.Embed(title="🚫 차단 완료", description=f"{member.mention} 차단됨\n사유: {reason}", color=0xC0392B)
        await ctx.send(embed=embed)
        await self.send_punish_log(ctx.guild, embed)

    @commands.command(name="unban")
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