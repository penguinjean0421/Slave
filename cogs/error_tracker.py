import discord
from discord.ext import commands
import logging
import os
from logging.handlers import TimedRotatingFileHandler

class ErrorTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        base_path = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(base_path, "..", "logs")

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger('discord_errors')
        self.logger.setLevel(logging.ERROR)

        log_file_path = os.path.join(log_dir, "error.log")

        handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when='midnight', 
            interval=1, 
            backupCount=30, 
            encoding='utf-8'
        )

        handler.suffix = "%Y-%m-%d"

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        embed = discord.Embed(
            title="⚠️ 에러 발생",
            description=f"`{str(error)}`",
            color=0xE74C3C
            )
        await ctx.send(embed=embed, delete_after=10)

        self.logger.error(
            f"Command: {ctx.command} | User: {ctx.author} ({ctx.author.id})", 
            exc_info=error
        )

async def setup(bot):
    await bot.add_cog(ErrorTracker(bot))