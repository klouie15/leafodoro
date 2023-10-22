# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import os
import discord
import nacl
import asyncio
import ffmpeg

from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

toDoList = []
global stopPomodoro
stopPomodoro = True
global timerOff
timerOff = True


# Create a function to get the bot to join the vc
@bot.command()
async def join(ctx):
  if ctx.author.voice:
    await ctx.send('You are in the voice channel')
    channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

  else:
    await ctx.send('Please join a voice channel first')


# @bot.command()
# async def testSound(ctx):
#     guild = ctx.guild
#     voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=guild)
#     audio_source = discord.FFmpegPCMAudio('airhorn.mp3')
#     if voice_client is not None:  # Check if voice_client is not None
#         if not voice_client.is_playing():
#             voice_client.play(audio_source, after=None)
#     else:
#         # Handle the case where voice_client is None (e.g., bot not connected to a voice channel)
#         await ctx.send("I'm not connected to a voice channel in this server.")


# Create a function to get the bot to leave the vc
@bot.command()
async def leave(ctx):
  if ctx.voice_client:
    await ctx.send('I am in voice')
    await ctx.guild.voice_client.disconnect()
  else:
    await ctx.send('Bot is not in a voice channel')


# General purpose timer used for both the remind and pomodoro commands
@bot.command()
async def timer(ctx, days, hrs, mins):
  end = int(days) * 86400 + int(hrs) * 3600 + int(mins) * 60
  await asyncio.sleep(end)
  global timerOff
  timerOff = True


# Set a reminder that pings the user after a certain timeframe
@bot.command()
async def remind(ctx, days, hrs, mins, activity):
  await ctx.send("Reminder set for " + activity + " in " + days + " days, " +
                 hrs + " hours, " + mins + " minutes, ")
  await timer(ctx, days, hrs, mins)
  await ctx.send(f"{ctx.author.mention} Reminder for **{activity}**")


@bot.command()
async def pomodoroStart(ctx, minsStudy, minsBreak):
  await join(ctx)
  await ctx.send(f"Timer started! You have {minsStudy} minutes to study!")
  await timer(ctx, 0, 0, minsStudy)
  global timerOff
  global stopPomodoro
  while (stopPomodoro):
    if (timerOff):
      await ctx.send(f"{ctx.author.mention} Break time!")
      await timer(ctx, 0, 0, minsBreak)

      timerOff = False
    else:
      await ctx.send(f"{ctx.author.mention} Study time!")
      await timer(ctx, 0, 0, minsStudy)


@bot.command()
async def pomodoroEnd(ctx):
  global stopPomodoro
  stopPomodoro = False
  await ctx.send('We are done studying')


# Adds an activity to the to-do list
@bot.command()
async def addtodo(ctx, *, args):
  toDoList.append(args)
  await ctx.send(f"Added **{args}** to the to-do list")


# Removes the desired activity from the to-do list, error if it does not exist
@bot.command()
async def removetodo(ctx, *, args):
  idx_to_remove = -1

  for i in range(len(toDoList)):
    if toDoList[i] == args:
      idx_to_remove = i

  if idx_to_remove != -1:
    toDoList.pop(idx_to_remove)
    await ctx.send(f"Removed **{args}** to the to-do list")
  else:
    await ctx.send(f"**{args}** is not in the to-do list")


# Prints the items in the to-do list in the order they were added
@bot.command()
async def todo(ctx):
  if len(toDoList) == 0:
    await ctx.send("There are no items in your to-do list")
  else:
    for i in range(len(toDoList)):
      await ctx.send(str(i + 1) + ". " + toDoList[i])


@bot.event
async def on_ready():
  print("Bot is connected")


try:
  load_dotenv()
  token = os.getenv('TOKEN') or ""
  if token == "":
    raise Exception("Please add your token to the Secrets pane.")
  bot.run(token)
except discord.HTTPException as e:
  if e.status == 429:
    print(
        "The Discord servers denied the connection for making too many requests"
    )
    print(
        "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
    )
  else:
    raise e
