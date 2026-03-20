import discord
from discord.ext import commands
from datetime import datetime
import json
import os

class System(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        self.config_file = "config.json"

        base_path = os.path.dirname(os.path.abspath(__file__)) # cogs 폴더 위치
        self.config_file = os.path.join(base_path, "..", "config.json") # 한 단계 위(Jean)의 config.json

        self.server_configs = {}
        self.load_config()

        self.bot_data = {
            "slave" : { 
                "name" : "Slave",
                "description" : "서버에 초대해 주셔서 감사합니다!\n", 
                "description1" : "즐거운 서버 활동을 돕기 위한 주요 명령어들을 안내해 드립니다.\n",
                "color" : 0x2b3137, 
            },
        }
    
    def load_config(self) :
    # 파일에서 모든 서버의 설정을 불러옴
        if os.path.exists(self.config_file) :
            with open(self.config_file, 'r', encoding = 'utf-8') as f:
                # { "서버ID": {"log": ID, "bot": ID}, ... } 구조
                self.server_configs = json.load(f)
        else:
            self.server_configs = {}

    def save_config(self) :
        # 현재 딕셔너리 상태를 파일에 저장
        with open(self.config_file, 'w', encoding = 'utf-8') as f:
            json.dump(self.server_configs, f, indent = 4, ensure_ascii=False)

    def get_server_data(self, guild) :
        """특정 서버의 설정 데이터를 가져오거나 갱신합니다."""
        gid = str(guild.id) # JSON 키는 문자열
        if gid not in self.server_configs :
            self.server_configs[gid] = {
                "server_name": guild.name,
                "owner_id": guild.owner_id,
                "log_channel_id" : None, 
                "command_channel_id" : None
            }
        else:
            # 실시간으로 이름과 서버장 정보 동기화
            self.server_configs[gid]["server_name"] = guild.name
            self.server_configs[gid]["owner_id"] = guild.owner_id
            
        return self.server_configs[gid]

    def get_log_channel(self, guild) :
        data = self.get_server_data(guild) 
        log_id = data.get("log_channel_id")
        
        if log_id :
            return self.bot.get_channel(log_id)
        return guild.system_channel
    
    async def cog_check(self, ctx) :
        data = self.get_server_data(ctx.guild)
        cmd_id = data.get("command_channel_id")

        if cmd_id and ctx.channel.id != cmd_id :
            if not ctx.author.guild_permissions.administrator :
                return False
        return True

# 명령어 채널 설정
    @commands.command(name = "set")
    @commands.has_permissions(administrator = True)
    async def set_command(self, ctx, target : str = None, channel : discord.TextChannel = None) :
        target = target.lower() if target else None
        target_channel = channel or ctx.channel
        gid = str(ctx.guild.id)

        # 서버 데이터 보장
        self.get_server_data(ctx.guild)

        if target == "log" :
            self.server_configs[gid]["log_channel_id"] = target_channel.id
            self.save_config()
            await ctx.send(f"✅ **로그 채널**이 {target_channel.mention}으로 설정되었습니다.")
        
        elif target == "bot" :
            self.server_configs[gid]["command_channel_id"] = target_channel.id
            self.save_config()
            await ctx.send(f"✅ **봇 명령어 채널**이 {target_channel.mention}으로 설정되었습니다. (관리자 제외)")
            
        else:
            embed = discord.Embed(title = "❓ 설정 명령어 사용법", color = 0xEEEEEE)
            embed.add_field(name = "로그 채널 설정", value = f"`{ctx.prefix}set log [#채널]`", inline = False)
            embed.add_field(name = "명령어 채널 설정", value = f"`{ctx.prefix}set bot [#채널]`", inline = False)
            await ctx.send(embed = embed)

    @set_command.error
    async def set_error(self, ctx, error) :
        if isinstance(error, commands.MissingPermissions) :
            await ctx.send("❌ 이 명령어를 사용할 권한(관리자)이 없습니다.")
        elif isinstance(error, commands.ChannelNotFound) :
            await ctx.send("❌ 해당 채널을 찾을 수 없습니다. 올바르게 언급(#채널)해 주세요.")

# 설정 해제
    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_command(self, ctx, target : str = None, channel : discord.TextChannel = None) :
        target = target.lower() if target else None
        target_channel = channel or ctx.channel
        gid = str(ctx.guild.id)

        # 서버 데이터 보장
        self.get_server_data(ctx.guild)
        
        if gid not in self.server_configs:
            return await ctx.send("❌ 설정된 데이터가 없습니다.")

        if target == "log" :
            self.server_configs[gid]["log_channel_id"] = None
            self.save_config()
            await ctx.send(f"✅ {target_channel.mention}은 이제 **로그채널**이 아닙니다.")
        
        elif target == "bot" :
            self.server_configs[gid]["command_channel_id"] = None
            self.save_config()
            await ctx.send(f"✅ {target_channel.mention}은 **봇 명령어 채널** 제한이 없습니다.")
            
        elif target == "all" :
            self.server_configs[gid] = {"log_channel_id": None, "command_channel_id": None}
            self.save_config()
            await ctx.send("🗑️ **이 서버의 모든 설정**이 초기화되었습니다.")

    @reset_command.error
    async def reset_error(self, ctx, error) :
        if isinstance(error, commands.MissingPermissions) :
            await ctx.send("❌ 이 명령어를 사용할 권한(관리자)이 없습니다.")

# 명령어 가이드
    async def send_welcome_help(self, channel, name) :
        # 명령어 도움말 임베드
        data = self.bot_data[name]
        embed = discord.Embed(
            title = f"👋 {data['name']} 입니다.",
            description = f"{data['description']} {data['description1']}",
            color = data['color']
        )

        embed.add_field(name = "🆔 Prefix", value = "æ", inline = False)
        embed.add_field(name = "📖 도움말", value = "`help`또는 `guide`", inline = False)
        embed.add_field(name = "⚙️ 채널설정(관리자 전용)", value = "`set [종류]`\n `reset [종류]`", inline = False)
        embed.add_field(name = "💻 누군가의 깃허브", value = "`github 과제`", inline = False)
        embed.add_field(name = "🛠️ 유틸리티", value = "`choose [A] [B]`\n", inline = False)
        embed.add_field(name = "🎁 히든 명령어", value = "찾아보시던가", inline = False)
        embed.set_thumbnail(url = self.bot.user.display_avatar.url)
        embed.set_footer(text = "상세 도움말은 æhelp 입력하세요.", icon_url = self.bot.user.display_avatar.url)
        await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild) :
        # 봇이 서버에 처음 들어왔을 때 실행
        channel = self.get_log_channel(guild)
        if channel and channel.permissions_for(guild.me).send_messages :
            await self.send_welcome_help(channel, "slave")

    @commands.command(name = "help", aliases = ["guide", "도움말"])
    async def manual_help(self, ctx) :
        # 사용자가 도움말 명령어를 쳤을 때 실행
        await self.send_welcome_help(ctx.channel, "slave")

# 서버 입퇴장 로그 기록
    @commands.Cog.listener()
    async def on_member_join(self, member) :
        channel = self.get_log_channel(member.guild)
        if channel :
            embed = discord.Embed(
                title = "📥 멤버 입장",
                description = f"{member.mention}(ID: {member.id}) 님이 서버에 입장했습니다.",
                color=0x00FF00,
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url = member.display_avatar.url)
            embed.set_footer(text = f"멤버 수 : {member.guild.member_count}명")
            await channel.send(embed =  embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member) :
        channel = self.get_log_channel(member.guild)
        if channel :
            embed = discord.Embed(
                title = "📤 멤버 퇴장",
                description = f"**{member.name}(ID: {member.id})** 님이 서버를 떠났습니다.",
                color = 0xFF0000,
                timestamp = datetime.now()
            )
            embed.set_footer(text = f"남은 멤버 수 : {member.guild.member_count}명")
            await channel.send(embed = embed)

# 메세지 수정 및 삭제
    @commands.Cog.listener()
    async def on_message_edit(self, before, after) :
        if before.author.bot or before.content == after.content :
            return
        channel = self.get_log_channel(before.guild)
        if channel :
            embed = discord.Embed(title = "📝 메시지 수정됨", url = after.jump_url, color = 0xFFA500, timestamp = datetime.now())
            embed.set_author(name = f"{before.author.name}(ID : {before.author.id})", icon_url = before.author.display_avatar.url)
            embed.add_field(name = "수정 전", value = f"```{before.content or '내용 없음'}```", inline = False)
            embed.add_field(name = "수정 후", value = f"```{after.content or '내용 없음'}```", inline = False)
            embed.set_footer(text = f"채널: #{before.channel.name}")
            await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message) :    
        if message.author.bot :
            return
        channel = self.get_log_channel(message.guild)
        if channel :
            embed = discord.Embed(title = "🗑️ 메시지 삭제됨", color = 0x333333, timestamp = datetime.now())
            embed.set_author(name = f"{message.author.name}(ID : {message.author.id})", icon_url = message.author.display_avatar.url)
            content = message.content if message.content else "내용 없음 (이미지/파일 등)"
            embed.add_field(name = "삭제된 내용", value=f"```{content}```", inline=False)
            embed.set_footer(text = f"채널: #{message.channel.name}")
            await channel.send(embed = embed)

#음성 채널 입퇴장
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after) :
        channel = self.get_log_channel(member.guild)
        if not channel : return
        if before.channel is None and after.channel is not None :
            embed = discord.Embed(description = f"🔊 {member.mention}(ID : {member.id}) 님이 **{after.channel.name}** 입장", color = 0x3498DB)
            await channel.send(embed = embed)
        elif before.channel is not None and after.channel is None :
            embed = discord.Embed(description = f"🔇 {member.mention}(ID : {member.id}) 님이 **{before.channel.name}** 퇴장", color = 0x95A5A6)
            await channel.send(embed = embed)
        elif before.channel != after.channel :
            embed = discord.Embed(description = f"🔄 {member.mention}(ID : {member.id}) : **{before.channel.name}** ➡ **{after.channel.name}**", color = 0x9B59B6)
            await channel.send(embed = embed)

async def setup(bot) :
    await bot.add_cog(System(bot))