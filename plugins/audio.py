import os
import tempfile
import subprocess
import sys
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
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

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

async def fix_thumb(thumb):
    width = 0
    height = 0
    try:
        if thumb != None:
            parser = createParser(thumb)
            metadata = extractMetadata(parser)
            if metadata and metadata.has("width"):
                width = metadata.get("width")
            if metadata and metadata.has("height"):
                height = metadata.get("height")
                
            with Image.open(thumb) as img:
                img = img.convert("RGB")
                if width > 0 and height > 0:
                    img = img.resize((width, height))
                img.save(thumb, "JPEG")
            parser.close()
    except Exception as e:
        logging.error(f"Error fixing thumbnail: {e}")
        thumb = None 
    return width, height, thumb

async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = f"{output_directory}/{time.time()}.jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss", str(ttl),
        "-i", video_file,
        "-vframes", "1",
        out_put_file_name
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if os.path.exists(out_put_file_name):
        return out_put_file_name
    return None

def set_thumbnail(video_file, thumbnail_file):
    command = [
        "ffmpeg",
        "-i", video_file,
        "-i", thumbnail_file,
        "-map", "0",
        "-map", "1",
        "-c", "copy",
        "-disposition:1", "attached_pic",
        video_file
    ]
    success, _ = run_command(command)
    return success

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
        logging.error(f"Error downloading media: {e}")
        return await ms.edit(f"An error occurred while downloading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False) 
    
    try:
        await ms.edit_text("Processing media...")

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file_no_audio = tempfile.mktemp(suffix=f"_{base_name}_noaudio.mp4")

        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(executor, remove_audio, file_path, output_file_no_audio)

        if success:
            # Take screenshot from the video
            screenshot = await take_screen_shot(file_path, tempfile.gettempdir(), ttl=5)
            if screenshot:
                # Fix and set the screenshot as the thumbnail
                _, _, fixed_thumb = await fix_thumb(screenshot)
                if fixed_thumb:
                    thumbnail_set = set_thumbnail(output_file_no_audio, fixed_thumb)
                    if thumbnail_set:
                        logging.info("Thumbnail set successfully.")
                    else:
                        logging.error("Failed to set thumbnail.")
                else:
                    logging.error("Failed to fix thumbnail.")
            else:
                logging.error("Failed to take screenshot.")
            
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
                caption=caption,
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
        logging.error(f"Error processing media: {e}")
        await message.reply_text(f"An error occurred: {e}")
