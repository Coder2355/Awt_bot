import os
import tempfile
import subprocess
import sys
import math
import time
import asyncio
import logging 
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from plugins import start
from helper.utils import progress_for_pyrogram
from plugins import extractor 
from pyrogram.errors import FloodWait

app = Flask(__name__)

# Thread pool for async processing
executor = ThreadPoolExecutor(max_workers=4)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr.decode('utf-8')}")
        return False, e.stderr.decode('utf-8')

def remove_audio(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-c:v', 'copy', '-an', '-map_metadata', '0', '-movflags', 'use_metadata_tags', output_file]
    success, _ = run_command(command)
    return success


async def get_video_details(file_path):
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size', '-of', 'default=noprint_wrappers=1', file_path]
    success, output = run_command(command)
    if success:
        details = {}
        for line in output.splitlines():
            key, value = line.split('=')
            details[key] = value
        return details
    return None

@Client.on_message(filters.command("remove_audio"))
async def handle_remove_audio(client, message):
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
        await message.reply_text("Please reply to a video or document message with the /remove_audio command.")
        return

    media = message.reply_to_message.video or message.reply_to_message.document
    ms = await message.reply_text("Downloading media...")

    try:
        file_path = await client.download_media(
            media, 
            progress=progress_for_pyrogram, 
            progress_args=("Downloading started..", ms, time.time())
        )
    except Exception as e:
        print(e)
        return await ms.edit(f"An error occured while downloading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False) 
    
    try:
        await ms.edit_text("Please wait processing...")

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file_no_audio = tempfile.mktemp(suffix=f"_{base_name}_noaudio.mp4")

        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(executor, remove_audio, file_path, output_file_no_audio)

        if success:
            details = await get_video_details(output_file_no_audio)
            if details:
                duration = details.get('duration', 'Unknown')
                size = details.get('size', 'Unknown')
                size_mb = round(int(size) / (1024 * 1024), 2)
                duration_sec = round(float(duration))
                caption = f"Here's your cleaned video file. Duration: {duration_sec} seconds. Size: {size_mb} MB"
                uploader = await ms.edit_text("Uploading media...")
            else:
                caption = "Here's your cleaned video file."
            
            await client.send_video(
                chat_id=message.chat.id,
                caption= caption,
                video=output_file_no_audio,
                progress=progress_for_pyrogram,
                progress_args=("Uploading...", uploader, time.time())
            )
        else:
            await message.reply_text("Failed to process the video. Please try again later.")
        
        await uploader.delete()

        # Safely remove files
        try:
            os.remove(file_path)
        except Exception as e:
            logging.error(f"Failed to remove file: {file_path}. Error: {e}")

        try:
            os.remove(output_file_no_audio)
        except Exception as e:
            logging.error(f"Failed to remove file: {output_file_no_audio}. Error: {e}")
            
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
