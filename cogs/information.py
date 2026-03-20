import discord
from discord.ext import commands

class Information(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        self.bot_data = {
            "bot" : { 
                "name" : "Slave",
                "description" : "서버에 초대해 주셔서 감사합니다!\n", 
                "description1" : "즐거운 서버 활동을 돕기 위한 주요 명령어들을 안내해 드립니다.\n",
                "color" : 0x2b3137, 
            },
        }

        self.credit_data = {
            "credit" : {
                "name" : "Slave",
                "developer" : "penguinjean0421",
                "illustrator" : "aram", 
                "supporter" : "목대 겜소과 친목 디코",
                "color" : 0x0f4c81, 
            },
        }

# 1. 통합된 도움말 명령어
    @commands.command(name="help", aliases = ["도움말", "guide"])
    async def help_command(self, ctx, category : str = None) :
        if category in ["관리자", "어드민", "admin", "management", "administrator"] :
            embed = discord.Embed(title = "🛠️ 서버 관리자 명령어 가이드", description = "서버 관리에 필요한 권한이 있는 멤버만 사용 가능한 명령어입니다.", color = 0xFF5555)
            embed.add_field(name = "🔇 음성 제재", value = "`mute [유저] [시간]` : 마이크 차단\n`unmute [유저]` : 마이크 해제\n`deafen [유저] [시간]` : 헤드셋 차단\n`vckick [유저]` : 음성 채널 강제 퇴장", inline = False)
            embed.add_field(name = "⏳ 채팅 제재", value = "`timeout [유저] [시간] [사유]` : 채팅 금지\n`untimeout [유저]` : 채팅 금지 해제", inline = False)
            embed.add_field(name = "🔨 서버 추방/차단", value = "`kick [유저] [사유]` : 서버에서 추방\n`ban [유저] [사유]` : 서버 영구 차단\n`unban [ID/닉네임]` : 차단 해제", inline = False)
            embed.add_field(name = "⚙️ 시스템 설정", value = "`set log` : 현재 채널을 로그 채널로 설정\n`set bot` : 현재 채널을 명령어 채널로 설정\n`reset all` : 서버 설정 초기화", inline = False)
            embed.set_footer(text = "시간 단위 예시: 10s(초), 5m(분), 1h(시간)")
            return await ctx.send(embed = embed)
        await self.send_welcome_help(ctx.channel, "bot")

    # 2. 공통 도움말 출력 함수
    async def send_welcome_help(self, channel, name):
        data = self.bot_data[name]
        embed = discord.Embed(
            title = f"👋 {data['name']} 입니다.",
            description = f"{data['description']} {data['description1']}",
            color = data['color']
        )
        embed.add_field(name = "🆔 Prefix", value = "`æ`", inline = True)
        embed.add_field(name = "📖 도움말", value = "`help` / `help 관리자`", inline = True)
        embed.add_field(name = "🛠️ 관리 기능", value = "상세 명령는 `æhelp 관리자` 참고", inline = False)
        embed.add_field(name = "💻 깃허브", value = "`github 과제`", inline = True)
        embed.add_field(name = "🛠️ 유틸리티", value = "`choose [A] [B]`", inline = True)
        embed.set_thumbnail(url = self.bot.user.display_avatar.url)
        embed.set_footer(text = "상세 도움말은 æhelp를 입력하세요.", icon_url = self.bot.user.display_avatar.url)
        await channel.send(embed = embed)

    # 3. 봇 입장 리스너
    @commands.Cog.listener()
    async def on_guild_join(self, guild) :
        channel = self.get_log_channel(guild)
        if channel and channel.permissions_for(guild.me).send_messages :
            await self.send_welcome_help(channel, "bot")

    # 크레딧 임베드
    async def send_credit_embed(self, ctx, name) :
        data = self.credit_data[name]
        embed = discord.Embed(title = f"Thanks for making {data['name']}", color = data['color'])
        embed.add_field(name = "Developer", value = f"[@{data['developer']}](https://www.github.com/{data['developer']})", inline = False)
        embed.add_field(name = "Illustrator", value = f"@{data['illustrator']}", inline = False)
        embed.add_field(name = "Supporter", value = f"목대 겜소과 친목 디코", inline = False)
        embed.add_field(name = "Soure Code", value = f"[바로가기](https://www.github.com/{data['developer']}/{data['name']})", inline = False)
        embed.add_field(name = "Contact", value = f"[제안 및 문의]({data['developer']}@gmail.com)", inline = False) 

        await ctx.send(embed = embed)

    @commands.command(name = "credit", aliases = ["크레딧"])
    async def credit(self, ctx):
        await self.send_credit_embed(ctx, "credit")

async def setup(bot) :
    await bot.add_cog(Information(bot))