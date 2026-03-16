import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random

# 토큰 가져오기
load_dotenv()
BOT_TOKEN = os.getenv(f'BOT_TOKEN', None)
if BOT_TOKEN is None :
    print('로드 실패')
else :
    print('로드 성공')  

# 봇 커맨드 설정
intents = discord.Intents.default()
intents.message_content = True
bot_command_prefix = "æ"
bot = commands.Bot(bot_command_prefix, intents = intents, help_command=None)

@bot.event
# 봇 상태 설정
async def on_ready(): 
    print(f'{bot.user.name} 봇이 온라인이 되었습니다!')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("penguinjæn Online"))

@bot.event
# 이름 입력시 구호나 인스타로 응답
async def on_message(message) :
    if message.content.startswith('aespa') or message.content.startswith('에스파'):
        await message.channel.send('Be my æ')
    if message.content.startswith('karina') or message.content.startswith('카리나') :
        await message.channel.send('@katarinabluu')
    if message.content.startswith('giselle') or message.content.startswith('지젤') :
        await message.channel.send('@aerichandesu')
    if message.content.startswith('winter') or message.content.startswith('윈터') :
        await message.channel.send('@imwinter')
    if message.content.startswith('ningning') or message.content.startswith('닝닝') :
        await message.channel.send('@imnotningning')
    await bot.process_commands(message)

@bot.command()
# 제시된 것중에 하나 선택
async def choose(ctx, *options) : 
    print('입력중')
    if len (options) < 2 :
        await ctx.send ("최소 2개이상의 선택지를 제시해라 좀.")
    else :
        select = random.choice(options)
        await ctx.send(f'{select}')

bot.run(BOT_TOKEN)