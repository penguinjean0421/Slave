import discord
from discord.ext import commands
import random

class Utility(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        # SNS Links
        self.member_data = {
            "aespa" : {
                "id" : "aespa_offical",
                "xiaohongshu" : "684e9fae000000001b0229c4",
                "weibo" : "7479199632",
                "youtube" : "aespa",
                "color" : 0x988eee, 
                "emoji" : "💜"
            },
            "karina" : {
                "id" : "katarinabluu", 
                "color" : 0x0000ff, 
                "emoji" : "💙"
            },
            "giselle": {
                "id" : "aerichandesu", 
                "color" : 0xff0000, 
                "emoji" : "🌙"
            },
            "winter" : {
                "id" : "imwinter", 
                "color" : 0x00ff00,
                "emoji" : "⭐️" 
            },
            "ningning": {
                "id" : "imnotningning", 
                "weibo" : "7842391335",
                "color" : 0xffff00, 
                "emoji" : "🦋"
            },
        }

    # 제시된 것중에 하나 선택
    @commands.command(name = "choose")
    async def choose(self, ctx, *options) : 
        if len (options) < 2 :
            await ctx.send ("최소 2개이상의 선택지를 제시해라 좀.")
        else :
            select = random.choice(options)
            await ctx.send(f"{select}")

    # SNS 임베드
    async def send_sns_embed(self, ctx, name) :
        data = self.member_data[name]
        embed = discord.Embed(
            title = f"{data['emoji']} Be my æ, {name}'s SNS",
            color = data['color']
        )   
        embed.add_field(name = "Instagram", value = f"[@{data['id']}](https://www.instagram.com/{data['id']})", inline = False)
        if name == "aespa" :
            embed.add_field(name = "Tiktok", value = f"[@{data['id']}](https://www.tiktok.com/@{data['id']})",inline = False )
            embed.add_field(name = "Weibo", value = f"[{name} Weibo 바로가기](https://weibo.com/u/{data['weibo']})", inline = False)
            embed.add_field(name = "X", value = f"[@{data['id']}](https://www.x.com/{data['id']})", inline = False)
            embed.add_field(name = "Xiaohongshu", value = f"[{name} Xiaohongshu 바로가기](https://www.xiaohongshu.com/user/profile/{data['xiaohongshu']})", inline = False)
            embed.add_field(name = "Youtube", value = f"[@{data['id']}](https://www.youtube.com/@{data['youtube']})", inline = False)
        if name == "ningning" :
            embed.add_field(name = "Weibo", value = f"[{name} Weibo 바로가기](https://weibo.com/u/{data['weibo']})", inline = False)
        await ctx.send(embed = embed)

    @commands.command(name = "aespa", aliases = ['에스파'])
    async def aespa(self, ctx):
        await self.send_sns_embed(ctx, "aespa")

    @commands.command(name = "karina", aliases = ['카리나'])
    async def karina(self, ctx):
        await self.send_sns_embed(ctx, "karina")

    @commands.command(name = "giselle", aliases = ['지젤'])
    async def giselle(self, ctx):
        await self.send_sns_embed(ctx, "giselle")

    @commands.command(name = "winter", aliases = [ '윈터'])
    async def winter(self, ctx):
        await self.send_sns_embed(ctx, "winter")

    @commands.command(name = "ningning", aliases = ['닝닝'])
    async def ningning(self, ctx):
        await self.send_sns_embed(ctx, "ningning")

async def setup(bot):
    await bot.add_cog(Utility(bot))