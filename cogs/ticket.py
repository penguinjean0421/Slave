import asyncio
import discord
from datetime import datetime, timezone
from discord.ext import commands


# 닫기 버튼이 포함된 View
class TicketCloseView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="티켓 닫기 🔒",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket_btn"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        channel = interaction.channel

        # 1. 먼저 버튼이 있는 메시지를 삭제합니다.
        try:
            await interaction.message.delete()
        except:
            pass # 이미 지워졌거나 권한이 없을 경우를 대비

        # 2. 채널 이름 변경 및 권한 수정
        await channel.edit(name=f"closed-{channel.name}")

        # 모든 멤버(관리자/봇 제외)의 읽기 권한 제거
        for member in channel.members:
            if not member.guild_permissions.administrator and not member.bot:
                await channel.set_permissions(member, overwrite=None)

        # 3. 종료 알림 전송
        # (이미 메시지를 삭제했으므로 response.send_message 대신 channel.send가 깔끔할 수 있습니다)
        close_embed = discord.Embed(
            description="이 티켓은 종료되었습니다.",
            color=0x2C3E50 # 아카이브 느낌의 어두운 회색
        )
        await channel.send(embed=close_embed)
        
        self.stop()

class TicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="티켓 열기 🎫",
        style=discord.ButtonStyle.primary,
        custom_id="open_ticket"
    )
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Ticket Cog 가져오기
        ticket_cog = self.bot.get_cog('Ticket')
        if ticket_cog:
            channel = await ticket_cog.open_ticket_logic(interaction.guild, interaction.user)
            await interaction.response.send_message(f"티켓이 생성되었습니다: {channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("티켓 시스템에 오류가 발생했습니다.", ephemeral=True)

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView(self.bot))
        self.bot.add_view(TicketCloseView(self.bot))

    # --- 공용 티켓 생성 로직 (버튼/명령어 공용) ---
    async def open_ticket_logic(self, guild, user):
        system_cog = self.bot.get_cog('System')
        
        log_channel = None
        if system_cog:
            config = system_cog.get_server_data(guild)
            current_count = config.get("ticket_count", 0) + 1
            config["ticket_count"] = current_count
            
            log_channel_id = config.get("log_channel_id")
            if log_channel_id:
                log_channel = guild.get_channel(log_channel_id)
            
            system_cog.save_config()
        else:
            current_count = 1

        ticket_name = f"ticket-{current_count:04d}"
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=ticket_name,
            overwrites=overwrites,
            reason=f"티켓 생성 (사용자: {user})"
        )

        embed = discord.Embed(
            title=f"**Ticket No. {current_count:04d}**",
            description=f"안녕하세요 {user.mention}님!\n문의 내용을 남겨주세요.\n\n**5분간 대화가 없으면 자동으로 닫힙니다.**",
            color=0x3498DB
        )
        await channel.send(embed=embed)

        # 로그 전송
        if log_channel:
            log_embed = discord.Embed(
                title="🎫 새 티켓 알림",
                color=0x3498DB,
                timestamp=datetime.now(timezone.utc)
            )
            log_embed.add_field(name="티켓 번호", value=f"#{current_count:04d}", inline=True)
            log_embed.add_field(name="생성자", value=f"{user.mention} ({user.id})", inline=True)
            log_embed.add_field(name="채널", value=channel.mention, inline=False)
            await log_channel.send(embed=log_embed)

        # 자동 종료 태스크 시작
        self.bot.loop.create_task(self.auto_close_timer(channel))
        return channel

    # 자동 종료 로직 분리
    async def auto_close_timer(self, channel):
        def check(m):
            return m.channel == channel
        
        while True:
            # [추가] 채널 이름이 이미 closed- 로 바뀌었다면 루프 종료
            if not channel.name.startswith("ticket-"):
                break

            try:
                # 300초(5분) 동안 메시지 대기
                await self.bot.wait_for('message', check=check, timeout=300.0)
            except asyncio.TimeoutError:
                # 타임아웃 발생 시 다시 한번 채널 이름 확인 (그 사이 수동 종료됐을 수 있음)
                if channel.name.startswith("ticket-"):
                    await channel.edit(name=f"closed-{channel.name}")
                    for member in channel.members:
                        if not member.guild_permissions.administrator and not member.bot:
                            await channel.set_permissions(member, overwrite=None)
                    
                    timeout_embed = discord.Embed(
                        title="⚠️ 자동 종료",
                        description="**5분 동안 대화가 없어 티켓이 자동으로 종료되었습니다.**",
                        color=0xE67E22
                    )
                    await channel.send(embed=timeout_embed)
                break # 타임아웃 후 종료되었으므로 루프 탈출
            except Exception:
                # 채널 삭제 등 예외 발생 시 루프 종료
                break
            else:
                # 메시지가 정상적으로 오면 다시 위로 올라가서 루프(타이머 리셋)
                continue

    async def send_ticket_panel(self, channel: discord.TextChannel):
        embed = discord.Embed(
            title="🎫 고객 지원 센터",
            description="문의 사항이 있으시면 아래 버튼을 눌러 티켓을 열어주세요.",
            color=0x3498DB
        )
        msg = await channel.send(embed=embed, view=TicketView(self.bot))
        return msg
    
    @commands.command(name="open")
    async def open_cmd(self, ctx):
        """!open 명령어로 티켓 생성"""
        # 생성 로직 호출
        channel = await self.open_ticket_logic(ctx.guild, ctx.author)
        embed=discord.Embed(
            description=f"✅ 티켓이 생성되었습니다: {channel.mention}",
            color=0xffffff
        )
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name="close")
    async def close_ticket_cmd(self, ctx):
        """!close 입력 시 닫기 버튼 전송"""
        if not ctx.channel.name.startswith("ticket-"):
            embed = discord.Embed(description="이 명령어는 티켓 채널에서만 사용할 수 있습니다.")
            return await ctx.send(embed=embed, delete_after=5)

        embed = discord.Embed(
            description="아래 버튼을 누르면 티켓이 종료되고 관리자 전용 채널로 변경됩니다.",
             color=0xE74C3C,
        )
        await ctx.send(embed=embed, view=TicketCloseView(self.bot))

    @commands.command(name="answer")
    @commands.has_permissions(administrator=True)
    async def reply_ticket(self, ctx, *, content: str):
        """관리자의 답변을 임베드로 전송"""
        if not (ctx.channel.name.startswith("ticket-") or ctx.channel.name.startswith("closed-")):
            return await ctx.send("이곳은 티켓 채널이 아닙니다.", delete_after=3)

        embed = discord.Embed(
            title="👤 관리자 답변",
            description=content,
            color=0x2ECC71,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.display_avatar.url
        )
        embed.set_footer(text="관리자")

        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # 여기에 자동 답변이나 추가 로직을 넣을 수 있습니다.
        pass


async def setup(bot):
    await bot.add_cog(Ticket(bot))