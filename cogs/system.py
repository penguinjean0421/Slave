import discord
from discord.ext import commands

class System(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        self.bot_data = {
            "slave" : { 
                "name" : "Slave",
                "description1" : "서버에 초대해 주셔서 감사합니다!\n", 
                "description2" : "즐거운 서버 활동을 돕기 위한 주요 명령어들을 안내해 드립니다.", 
                "color" : 0x2b3137, 
            },
        }

    @commands.Cog.listener()
    async def on_guild_join(self, guild) :
        target_channel = guild.system_channel
        if target_channel is None or not target_channel.permissions_for(guild.me).send_messages :
            for channel in guild.text_channels :
                if channel.permissions_for(guild.me).send_messages :
                    target_channel = channel
                    break

        if target_channel:
            await self.send_welcome_help(target_channel, "slave")

    async def send_welcome_help(self, channel, name) :
        data = self.bot_data[name]
        embed = discord.Embed(
            title = f"👋 {data['name']} 입니다.",
            description = f"{data['description1']} {data['description2']}",
            color = data['color']
        )

        embed.add_field(name = "⌨️ Prefix", value = "**æ**, ???, ???", inline = False)
        embed.add_field(name = "📂 누군가의 깃허브", value = "`github 과제`", inline = True)
        embed.add_field(name = "🤔 유틸리티", value = "`choose [A] [B]`\n ``", inline = True)
        embed.add_field(name = "✨ 히든 명령어", value = "제작자가 좋아하는 것을 입력해 보아요 ...", inline = False)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text= "상세 도움말은 æhelp 입력하세요.", icon_url=self.bot.user.display_avatar.url)
        await channel.send(embed=embed)

    @commands.command(name= "도움말", aliases=["help", "guide"])
    async def manual_help(self, ctx) :
        await self.send_welcome_help(ctx.channel, "slave")

async def setup(bot) :
    await bot.add_cog(System(bot))