# KickFix-Discord-Bot
Post a kick clip link and the bot will upload the clip video to the chat.

Tries to upload videos as fast as possible.

-If a .mp4 of the entire clip can be fetched from Kick, it will just send the link to that mp4. (Nearly instantaneous)

-Otherwise, it will need to download all the .ts segments the clip is composed of, combine them, and convert to mp4 before uploading. (takes some time)

-Longer clips need to get automatically compressed before they can be uploaded.

-After the clip has been served once, the video link will be cached so it can be served faster the next time.
