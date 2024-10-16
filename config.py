import os, time

class Config(object):
    #Audio-_edit_bot client Config 
    API_ID = os.getenv("API_ID", "21740783")
    API_HASH = os.getenv("API_HASH", "a5dc7fec8302615f5b441ec5e238cd46")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "6610201435:AAHEv2YoM2ZEtlEdqjilv9mZGjT9Uzzrntw")
    AUTH_USERS = set(int(x) for x in os.environ.get("AUTH_USERS", "6299192020").split())


    #port to run web server
    PORT = int(os.getenv('PORT', "8050"))

    # database config
    DB_NAME = os.environ.get("DB_NAME","Speedwolf1")     
    DB_URL  = os.environ.get("DB_URL","mongodb+srv://Speedwolf1:speedwolf24689@cluster0.rgfywsf.mongodb.net/")


    # other configs
    BOT_UPTIME  = time.time()
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
    START_PIC   = os.environ.get("START_PIC", "https://telegra.ph/file/feb6dd0a1cb8576943c0f.jpg")

    # wes response configuration     
    WEBHOOK = bool(os.environ.get("WEBHOOK", "True"))

    
class Txt(object):
    
    START_TXT = """Hello Friends i am The Advance 📹Video Editor bot i have special Features like "Audio remover" and "video trimmer" 
    
</a>"\n Bot Is Made By @Anime_Warrior_Tamil"</b>"""
    
    ABOUT_TXT = f"""<b>😈 My Name :</b> <a href='https://t.me/Gjjbsrijjb_bot'>Video editor bot ⚡</a>
<b>📝 Language :</b> <a href='https://python.org'>Python 3</a>
<b>📚 Library :</b> <a href='https://pyrogram.org'>Pyrogram 2.0</a>
<b>🚀 Server :</b> <a href='https://heroku.com'>Heroku</a>
<b>📢 Channel :</b> <a href='https://t.me/Anime_Warrior_Tamil'>AWT BOTS</a>
<b>🛡️ :</b> <a href='https://t.me/+NITVxLchQhYzNGZl'>AWT Developer</a>
    
<b>😈 Bot Made By :</b> @AWT_Bot_Developer"""


    HELP_TXT = """
 <b><u>Video Editor bot Commands</u></b>
  
<b>•»</b> /start Use this command to Check bot is alive ✅.
<b>•»</b> /remove_audio Uꜱᴇ This Command to remove audio.
<b>•»</b> /trim_video Use this command to Trim video.

✏️ <b><u>Hᴏᴡ Tᴏ use bot</u></b>

<b>•»</b> Reply to a video to remove audio or trim video          

ℹ️ 𝗔𝗻𝘆 𝗢𝘁𝗵𝗲𝗿 𝗛𝗲𝗹𝗽 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 :- <a href=https://t.me/AWT_bots_developer>𝘽𝙤𝙩 𝘿𝙚𝙫𝙚𝙡𝙤𝙥𝙚𝙧</a>
"""

#⚠️ Dᴏɴ'ᴛ Rᴇᴍᴏᴠᴇ Oᴜʀ Cʀᴇᴅɪᴛꜱ @ILLGELA_DEVELOPER🙏🥲
    DEV_TXT = """hiiiiiiiiiii"""
    
    PROGRESS_BAR = """\n
<b>📁 Size</b> : {1} | {2}
<b>⏳️ Done</b> : {0}%
<b>🚀 Speed</b> : {3}/s
<b>⏰️ ETA</b> : {4} """



#This bot was created by Awt botz
