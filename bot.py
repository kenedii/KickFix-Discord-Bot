# bot.py
import os
import random
import discord
import json
from discord.ext import commands
from dotenv import load_dotenv
import sys
import datetime
import time
import videoUtils
import re
import pickle

load_dotenv('credentials.env')

BOT_TOKEN = os.getenv('BOT_TOKEN')
cache = {}
#UPLOAD_AUTHORITY = os.getenv('UPLOAD_AUTHORITY') # This user will upload the clip to Discord's servers

def extract_kick_clip_link(message_content):
    # Define the regular expression pattern to match the link
    pattern = r'https://kick\.com/[^\s?]+\?clip=clip_[A-Za-z0-9]+'
    
    # Search for the pattern in the message content
    match = re.search(pattern, message_content)
    
    # If a match is found, return the matched link, else return None
    if match:
        print(match.group(0))
        return match.group(0)
    return None

def cache_video_link(clip_url, video_link, action='Update'):
    if action == 'Update':
        cache[clip_url] = video_link
        with open('videolinks_cache.pkl', 'wb') as file:
            pickle.dump(cache, file)
    elif action == 'Load':
        with open('videolinks_cache.pkl', 'rb') as file:
            cache = pickle.load(file)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} is online.')
    activity = discord.Game(name="Post a kick link and I will fix it!")
    await client.change_presence(status=discord.Status.online, activity=activity)

async def handle_message(message):
    if "?clip=clip_" in message.content and "kick.com" in message.content:
        print('link detected')
        clip_link = extract_kick_clip_link(message.content)
        if clip_link in cache:
            await message.channel.send(cache[clip_link])
        elif clip_link is not None:
            filename = videoUtils.download_clip(clip_link)
            sent_video = await message.channel.send(file=discord.File(filename))
            file_url = sent_video.attachments[0].url
            cache_video_link(clip_link, file_url)
        return
    
@client.event
async def on_message(message):
    await handle_message(message)

cache_video_link(None, None, action='Load')
client.run(BOT_TOKEN)
