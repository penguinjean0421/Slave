import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class MyBot(commands.Bot) :
    def __init__(self) :
        raw_prefixes = os.getenv("BOT_PREFIXES", "æ")
        prefixes = [p.strip() for p in raw_prefixes.split(",")]
        intents = discord.Intents.default()
        intents.members = True         
        intents.message_content = True
        intents.voice_states = True
        super().__init__(command_prefix = prefixes, intents = intents, help_command = None)

    # cogs 폴더 내의 모든 .py 파일을 로드
    async def setup_hook(self) :
        base_path = Path(__file__).parent
        cogs_path = base_path / "cogs"
        for filename in os.listdir(cogs_path) :
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"{filename} 로드 완료!")

    async def on_ready(self):
        print(f"{self.user.name} 온라인!(Prefix : {self.command_prefix})")
        await self.change_presence(activity=discord.Game("No name"))

async def main() :
    bot = MyBot()
    async with bot :
        await bot.start(os.getenv("BOT_TOKEN"))

if __name__ == "__main__" :
    asyncio.run(main())