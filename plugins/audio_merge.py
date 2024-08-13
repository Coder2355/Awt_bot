import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import subprocess
import time
from config import API_ID, API_HASH, BOT_TOKEN
from progress import progress

DOWNLOAD_DIR = "/content/Drive_bot/Drive_bot/downloads/"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

user_media_files = {}
user_merge_mode = {}

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB in bytes

app = Client("media_merger_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "Welcome! You can use the following commands:\n"
        "/merge_audio - Merge two audio files.\n"
        "/merge_video - Merge a video file with an audio file (only for files below 2GB)."
    )

@app.on_message(filters.command("merge_audio"))
async def set_merge_audio(client, message: Message):

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import subprocess
import time
from config import API_ID, API_HASH, BOT_TOKEN
from progress import progress

DOWNLOAD_DIR = "/content/Drive_bot/Drive_bot/downloads/"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

user_media_files = {}
user_merge_mode = {}

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB in bytes

app = Client("media_merger_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "Welcome! You can use the following commands:\n"
        "/merge_audio - Merge two audio files.\n"
        "/merge_video - Merge a video file with an audio file (only for files below 2GB)."
    )

@app.on_message(filters.command("merge_audio"))
async def set_merge_audio(client, message: Message):
    user_id = message.from_user.id
    user_merge_mode[user_id] = "audio"
    user_media_files[user_id] = []
    await message.reply_text("Send the first audio file.")

@app.on_message(filters.command("merge_video"))
async def set_merge_video(client, message: Message):
    user_id = message.from_user.id
    user_merge_mode[user_id] = "video"
    user_media_files[user_id] = []
    await message.reply_text("Send the video file.")

@app.on_message((filters.video | filters.audio) & ~filters.forwarded)
async def receive_media(client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_merge_mode:
        await message.reply_text("Please use /merge_audio or /merge_video to start the merging process.")
        return

    merge_mode = user_merge_mode[user_id]
    media_type = 'audio' if message.audio else 'video'
    media_file = getattr(message, media_type)

    # Check file size
    if media_file.file_size > MAX_FILE_SIZE:
        await message.reply_text(f"The file is too large (over 2GB). Please provide a smaller file.")
        return

    start_time = time.time()
    progress_message = await message.reply_text(f"Downloading {media_type}...")

    try:
        media_path = await message.download(
            file_name=f"{DOWNLOAD_DIR}{media_file.file_name}",
            progress=progress,
            progress_args=(progress_message, start_time, f"Downloading {media_type}")
        )

        user_media_files[user_id].append(media_path)
        await asyncio.sleep(1)  # Added delay

        if merge_mode == "audio":
            if len(user_media_files[user_id]) == 1:
                await progress_message.edit_text("First audio received. Now send the second audio.")
            elif len(user_media_files[user_id]) == 2:
                await progress_message.edit_text("Both audios received. Merging them now...")
                await merge_audios(client, message, user_id)
        elif merge_mode == "video":
            if len(user_media_files[user_id]) == 1 and media_type == "video":
                await progress_message.edit_text("Video received. Now send the audio file.")
            elif len(user_media_files[user_id]) == 2 and any('.mp4' in file for file in user_media_files[user_id]):
                await progress_message.edit_text("Both video and audio received. Merging them now...")
                await merge_video_and_audio(client, message, user_id)
    except Exception as e:
        await progress_message.edit_text(f"Error during download: {e}")
        print(f"Error during download: {e}")  # Debugging statement

async def merge_audios(client, message, user_id):
    audio1, audio2 = user_media_files[user_id]
    output_path = f"{DOWNLOAD_DIR}merged_audio_{user_id}.mp3"

    command = [
        "ffmpeg",
        "-y",  # Add the '-y' flag to overwrite existing files
        "-i", audio1,
        "-i", audio2,
        "-filter_complex", "[0:0][1:0]concat=n=2:v=0:a=1[out]",
        "-map", "[out]",
        output_path
    ]

    start_time = time.time()
    progress_message = await message.reply_text("Merging audio files...")

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        if os.path.exists(output_path):
            await progress_message.edit_text("Merging complete, uploading the merged audio...")
            await asyncio.sleep(1)  # Added delay before upload
            try:
                await message.reply_document(
                    document=output_path,
                    caption="Here is your merged audio file!",
                    progress=progress,
                    progress_args=(progress_message, start_time, "Uploading merged audio")
                )
            except Exception as e:
                await progress_message.edit_text(f"Failed to upload the merged audio: {e}")
                print(f"Failed to upload the merged audio: {e}")  # Debugging statement
        else:
            await progress_message.edit_text("Merging completed, but the output file was not found.")
    else:
        await progress_message.edit_text(f"Failed to merge: {stderr.decode()}")
        print(f"Failed to merge: {stderr.decode()}")  # Debugging statement

    # Clean up
    os.remove(audio1)
    os.remove(audio2)
    if os.path.exists(output_path):
        os.remove(output_path)

    # Remove user data
    del user_media_files[user_id]
    del user_merge_mode[user_id]

async def merge_video_and_audio(client, message, user_id):
    video, audio = user_media_files[user_id]
    output_path = f"{DOWNLOAD_DIR}merged_video_{user_id}.mp4"

    command = [
        "ffmpeg",
        "-y",  # Add the '-y' flag to overwrite existing files
        "-i", video,
        "-i", audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        output_path
    ]

    start_time = time.time()
    progress_message = await message.reply_text("Merging video and audio...")

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        if os.path.exists(output_path):
            await progress_message.edit_text("Merging complete, uploading the merged video...")
            await asyncio.sleep(1)  # Added delay before upload
            try:
                await message.reply_document(
                    document=output_path,
                    caption="Here is your merged video file!",
                    progress=progress,
                    progress_args=(progress_message, start_time, "Uploading merged video")
                )
            except Exception as e:
                await progress_message.edit_text(f"Failed to upload the merged video: {e}")
                print(f"Failed to upload the merged video: {e}")  # Debugging statement
        else:
            await progress_message.edit_text("Merging completed, but the output file was not found.")
    else:
        await progress_message.edit_text(f"Failed to merge: {stderr.decode()}")
        print(f"Failed to merge: {stderr.decode()}")  # Debugging statement

    # Clean up
    os.remove(video)
    os.remove(audio)
    if os.path.exists(output_path):
        os.remove(output_path)

    # Remove user data
    del user_media_files[user_id]
    del user_merge_mode[user_id]
                    
