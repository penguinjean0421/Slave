import discord
from discord.ext import commands

class Information(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        self.help_data = {
            "bot" : { 
                "name" : "Slave",
                "greeting" : "서버에 초대해 주셔서 감사합니다!\n", 
                "summary" : "즐거운 서버 활동을 돕기 위한 주요 명령어들을 안내해 드립니다.\n",
                "theme_color" : 0x007acc,
            },
        }

        self.credit_data = {
            "credit" : {
                "bot_name" : "Slave",
                "developer" : "penguinjean0421",
                "illustrator" : "aram", 
                "supporter" : "목대 겜소과 친목 디코",
                "theme_color" : 0x5d2b90, 
            },
        }

    @commands.command(name="help", aliases=["도움말", "guide"])
    async def help_command(self, ctx, category: str = None):
        prefix = ctx.prefix
        admin_keywords = ["관리자", "어드민", "admin", "management", "administrator"]
        if category and category.lower() in admin_keywords:
            return await self.send_admin_help(ctx.channel, prefix)
        await self.send_welcome_help(ctx.channel, "bot", prefix)

    async def send_welcome_help(self, channel, name, prefix = None):
        data = self.help_data[name]
        if prefix is None:
            prefix = self.bot.command_prefix
            if isinstance(prefix, list): prefix = prefix[0]

        embed = discord.Embed(title = f"👋 {data['name']} 입니다.", description = f"{data['greeting']}{data['summary']}", color = data['theme_color'])
        embed.add_field(name = "🆔 접두사(Prefix)", value = f"`{prefix}`", inline = False)
        embed.add_field(name = "📖 도움말 명령어", value = f"`{prefix}help` / `{prefix}help 관리자`", inline = False)
        embed.add_field(name = "⚙️ 서버 관리", value = f"상세 명령은 `{prefix}help 관리자` 참고", inline = False)        
        embed.add_field(name = "💻 오픈소스", value = f"`{prefix}github 과제`", inline = False)
        embed.add_field(name = "✨ 유틸리티", value = f"`{prefix}choose [A] [B]`\n `{prefix}menu [종류]`", inline = False)
        embed.set_thumbnail(url = self.bot.user.display_avatar.url)
        embed.set_footer(text = f"상세 도움말은 {prefix}help를 입력하세요.", icon_url = self.bot.user.display_avatar.url)
        
        await channel.send(embed = embed)

    async def send_admin_help(self, channel, prefix):
        embed = discord.Embed(
            title="🛠️ 서버 관리자 명령어 가이드", 
            description="서버 관리 권한이 있는 멤버만 사용 가능한 명령어입니다.", 
            color=0xFF5555
        )
        embed.add_field(
            name="🔇 음성 제재", 
            value=f"`{prefix}mute [유저] (시간)` : 마이크 차단\n"
                  f"`{prefix}unmute [유저]` : 마이크 해제\n"
                  f"`{prefix}deafen [유저] (시간)` : 헤드셋 차단\n"
                  f"`{prefix}undeafen [유저]` : 헤드셋 해제\n"
                  f"`{prefix}vckick [유저] (사유)` : 음성 채널 강제 퇴장", 
            inline=False
        )
        embed.add_field(
            name="🔨 서버 제재", 
            value=f"`{prefix}timeout [유저] [시간] (사유)` : 채팅 금지 (타임아웃)\n"
                  f"`{prefix}kick [유저] (사유)` : 서버에서 추방\n"
                  f"`{prefix}ban [유저] (사유)` : 서버 영구 차단\n"
                  f"`{prefix}unban [ID/닉네임]` : 차단 해제", 
            inline=False
        )
        embed.add_field(
            name="⚙️ 시스템 설정", 
            value=f"`{prefix}set [log/punish/bot] [#채널]` : 특정 채널 설정\n"
                  f"`{prefix}reset [log/punish/bot]` : 특정 설정 초기화\n"
                  f"`{prefix}reset all` : 서버의 모든 설정 초기화", 
            inline=False
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text="시간 단위: s(초), m(분), h(시간), d(일) | 예: 10m, 1d", 
            icon_url=self.bot.user.display_avatar.url
        )
        await channel.send(embed=embed)

    async def send_credit(self, ctx, name) :
        data = self.credit_data[name]
        embed = discord.Embed(
            title = f"Thanks for using {data['bot_name']}", 
            description=f"{data['bot_name']}를 함께 만들어주신 분들입니다.",
            color = data['theme_color'],
            )
        
        embed.add_field(name="👤 Developer", value=f"[{data['developer']}](https://github.com/{data['developer']})", inline=True)
        embed.add_field(name="🎨 Illustrator", value=f"@{data['illustrator']}", inline=True)
        embed.add_field(name="🤝 Supporter", value=data['supporter'], inline=False)
        embed.add_field(name="🔗 Source Code", value=f"[GitHub Repository](https://github.com/{data['developer']}/{data['bot_name']})", inline=False)
        embed.add_field(name="📧 Contact", value=f"`{data['developer']}@gmail.com`", inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"© 2026 {data['developer']} All rights reserved.")
        await ctx.send(embed = embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild) :
        system_cog = self.bot.get_cog('System')
        if system_cog: channel = system_cog.get_log_channel(guild)
        if channel and channel.permissions_for(guild.me).send_messages :
            await self.send_welcome_help(channel, "bot")

    @commands.command(name = "credit", aliases = ["크레딧"])
    async def credit(self, ctx):
        await self.send_credit(ctx, "credit")

async def setup(bot) :
    await bot.add_cog(Information(bot))