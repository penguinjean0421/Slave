import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

class MyBot(commands.Bot) :
    def __init__(self) :
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="æ", intents=intents, help_command=None)

    async def setup_hook(self) :
        # cogs 폴더 내의 모든 .py 파일을 로드
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"{filename} 로드 완료!")

    async def on_ready(self):
        print(f"{self.user.name} 온라인!")
        await self.change_presence(activity=discord.Game("No name"))

async def main() :
    load_dotenv()
    bot = MyBot()
    async with bot:
        await bot.start(os.getenv("BOT_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())