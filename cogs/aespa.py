import discord
from discord.ext import commands

class Aespa(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        # SNS Links
        self.aespa_data = {
            "aespa" : {
                "id" : "aespa_offical",
                "id1" : "aespa.offical", 
                "pinterest" : "aespicyclub",
                "jptwitter" : "aespaJPofficial",
                "bilibili" : "2128487337",
                "douyin" : "h5ANeSK5EN8",
                "weibo" : "7479199632",
                "xiaohongshu": "684e9fae000000001b0229c4",
                "color" : 0x988eee, 
                "emoji" : "💜"
            },
            "karina" : {
                "instagram" : "katarinabluu", 
                "color" : 0x0000ff, 
                "emoji" : "💙"
            },
            "giselle": {
                "instagram" : "aerichandesu", 
                "color" : 0xff0000, 
                "emoji" : "🌙"
            },
            "winter" : {
                "instagram" : "imwinter", 
                "color" : 0x00ff00,
                "emoji" : "⭐️" 
            },
            "ningning": {
                "instagram" : "imnotningning", 
                "weibo" : "7842391335",
                "color" : 0xffff00, 
                "emoji" : "🦋"
            },
        }

    # SNS 임베드
    async def send_sns_embed(self, ctx, name, region = None) :
        data = self.aespa_data[name]
        if name == "aespa" :
            embed = discord.Embed(
            title = f"{data['emoji']} Be my æ, {name}'s SNS",
            color = data['color']
            )

            if region in ["kr", "kor", "korea", "대한민국", "한국"] :
                embed.add_field(name = "Instagram", value = f"[바로가기](https://www.instagram.com/{data['id']})", inline = True)
                embed.add_field(name = "Tiktok", value = f"[바로가기](https://www.tiktok.com/@{data['id1']})",inline = True)
                embed.add_field(name = "Twitter", value = f"[바로가기](https://www.x.com/{data['id']})", inline = True)
                embed.add_field(name = "Pinterest", value = f"[바로가기](https://pinterest.com/{name})", inline = True)
                embed.add_field(name = "Snapchat", value = f"[바로가기](https://www.snapchat.com/@{data['id1']})", inline = True)

            elif region in ["cn", "china", "중국"] :
                embed.add_field(name = "BiliBili", value = f"[바로가기](https://space.bilibili.com/{data['bilibili']})", inline = True)
                embed.add_field(name = "Douyin", value = f"[바로가기](https://v.douyin.com/{data['douyin']})", inline = True)
                embed.add_field(name = "Weibo", value = f"[바로가기](https://weibo.com/u/{data['weibo']})", inline = True)
                embed.add_field(name = "Xiaohongshu", value = f"[바로가기](https://www.xiaohongshu.com/user/profile/{data['xiaohongshu']})", inline = True)
            
            elif region in ["jp", "japan", "일본"] :
                embed.add_field(name = "🇯🇵 Offical Twitter", value = f"[바로가기](https://www.x.com/{data['jptwitter']})", inline = False)
            
            else :
                embed = discord.Embed(
                title = f"{data['emoji']} Be my æ, {name}'s Community",
                color = data['color']
                )
                embed.add_field(name = "Homepage", value = f"[바로가기](https://{name}.com)", inline = True)
                embed.add_field(name = "Weverse", value = f"[바로가기](https://weverse.io/{name})", inline = True)
                embed.add_field(name = "Youtube", value = f"[바로가기](https://www.youtube.com/@{name})", inline = True)

        elif name in ["karina", "giselle", "winter"] : 
            embed.add_field(name = "Instagram", value = f"[@{data['instagram']}](https://www.instagram.com/{data['instagram']})", inline = False)

        elif name == "ningning" :
            embed.add_field(name = "Instagram", value = f"[@{data['instagram']}](https://www.instagram.com/{data['instagram']})", inline = False)
            embed.add_field(name = "Weibo", value = f"[{name} Weibo 바로가기](https://weibo.com/u/{data['weibo']})", inline = False)

        await ctx.send(embed = embed)

    @commands.command(name = "aespa", aliases = ['에스파'])
    async def aespa(self, ctx, region : str = None):
        search_region = region.lower().strip() if region else None
        await self.send_sns_embed(ctx, "aespa", search_region)

    @commands.command(name = "karina", aliases = ['카리나'])
    async def karina(self, ctx) :
        await self.send_sns_embed(ctx, "karina")

    @commands.command(name = "giselle", aliases = ['지젤'])
    async def giselle(self, ctx) :
        await self.send_sns_embed(ctx, "giselle")

    @commands.command(name = "winter", aliases = [ '윈터'])
    async def winter(self, ctx) :
        await self.send_sns_embed(ctx, "winter")

    @commands.command(name = "ningning", aliases = ['닝닝'])
    async def ningning(self, ctx) :
        await self.send_sns_embed(ctx, "ningning")

async def setup(bot) :
    await bot.add_cog(Aespa(bot))