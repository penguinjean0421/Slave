import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Slave(commands.Bot) :
    def __init__(self) :
        raw_prefixes = os.getenv("BOT_PREFIXES")
        prefixes = [p.strip() for p in raw_prefixes.split(",")]

        intents = discord.Intents.default()
        intents.members = True         
        intents.message_content = True
        intents.voice_states = True

        super().__init__(command_prefix = prefixes, intents = intents, help_command = None)

    # cogs 폴더 내의 모든 .py 파일을 로드
    async def setup_hook(self) :
        cogs_path = Path(__file__).parent / "cogs"
        for filepath in cogs_path.glob("*.py"):
            cog_name = f"cogs.{filepath.stem}"
            try:
                await self.load_extension(cog_name)
                print(f"✅ {cog_name} 로드 성공")
            except Exception as e:
                print(f"❌ {cog_name} 로드 실패 -> {e}")

    async def on_ready(self):
        print(f"🟢 {self.user.name} Online, (Prefix : {', '.join(self.command_prefix)})")
        await self.change_presence(activity=discord.Game("Noot Noot"))

async def main() :
    bot = Slave()
    async with bot :
        await bot.start(os.getenv("BOT_TOKEN"))

if __name__ == "__main__" :
    asyncio.run(main())