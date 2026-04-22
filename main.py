import asyncio
import os
import logging
from pathlib import Path
from typing import List

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()



class Slave(commands.Bot):
    def __init__(self):
        raw_prefixes = os.getenv("BOT_PREFIXES")
        prefixes: List[str] = [p.strip() for p in raw_prefixes.split(",")] if raw_prefixes else ["!"]

        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.voice_states = True

        super().__init__(
            command_prefix=prefixes,
            intents=intents,
            help_command=None
        )

        self.logger = logging.getLogger('discord_errors')

    async def setup_hook(self):
        cogs_path = Path(__file__).parent / "cogs"
        if not cogs_path.exists():
            cogs_path.mkdir()
            print("📂 'cogs' 폴더가 없어 새로 생성했습니다.")
        
        for filepath in cogs_path.glob("*.py"):
            if filepath.stem.startswith("__"):
                continue
            cog_name = f"cogs.{filepath.stem}"
            try:
                await self.load_extension(cog_name)
                print(f"✅ {cog_name} 로드 성공")
            except Exception as e:
                self.logger.error(f"코그 로드 실패 ({cog_name}): {e}", exc_info=True)
                print(f"❌ {cog_name} 로드 실패 -> 로그를 확인하세요.")

    async def on_ready(self):
        print("-" * 30)
        print(f"🟢 {self.user.name} 온라인!")
        print(f"🆔 ID: {self.user.id}")
        print(f"🔢 접두사: {', '.join(self.command_prefix)}")
        print("-" * 30)
        await self.change_presence()

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """명령어 성공 시 유저 메시지 삭제 (권한 에러 방어)"""
        try:
            if ctx.guild and ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()
        except Exception as e:
            self.logger.warning(f"명령어 완료 후 메시지 삭제 실패: {e}")

async def main():
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
        handlers=[
            logging.FileHandler(filename='logs/error.log', encoding='utf-8', mode='a'),
            logging.StreamHandler()
        ]
    )
    
    main_logger = logging.getLogger('discord_errors')
    bot = Slave()
    token = os.getenv("BOT_TOKEN")

    if not token:
        main_logger.critical("BOT_TOKEN이 .env 파일에 존재하지 않습니다.")
        return

    async with bot:
        try:
            await bot.start(token)
        except discord.LoginFailure:
            main_logger.critical("토큰이 유효하지 않습니다. 로그인에 실패했습니다.")
        except Exception as e:
            main_logger.error(f"봇 실행 중 치명적 오류 발생: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🚩 키보드 입력으로 인해 봇을 종료합니다.")
    except Exception as e:
        logging.getLogger('discord_errors').critical(f"시스템 예외 발생: {e}", exc_info=True)