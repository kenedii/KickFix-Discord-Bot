# KickFix-Discord-Bot

Post a kick.com clip link and the bot will upload the clip video to the chat.

Invite this bot to your server:
# https://discord.com/oauth2/authorize?client_id=1253549903091728384&permissions=116736&scope=bot 

Tries to upload videos as fast as possible.

-If a .mp4 of the entire clip can be fetched from Kick, it will just send the link to that mp4. (Nearly instantaneous)

-Otherwise, it will need to download all the .ts segments the clip is composed of, combine them, and convert to mp4 before uploading. (takes some time)

-Clips get automatically compressed before they are uploaded.

-After the clip has been served once, the video link will be cached so it can be served faster the next time.

### Dependencies

* Python
  
* pip install discord
  
* pip install python-dotenv

* FFMPEG

*The versions used for this project are: Python 3.11.5, discord 2.3.2, python-dotenv 1.0.1, ffmpeg 4.2.2*

### Executing program

- Create a text file 'credentials.env' and write ```BOT_TOKEN = "INSERT_TOKEN_HERE"``` inside
- Run bot.py
