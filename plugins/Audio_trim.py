import os
import asyncio
import subprocess
from pyrogram import Client, filters
from flask import Flask
from threading import Thread
from config import Config

# Initialize Flask
flask_app = Flask(__name__)

# Function to trim audio using FFmpeg
async def trim_audio(input_file, output_file, start_time, end_time):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', start_time,
        '-to', end_time,
        '-c:a', 'copy',  # Use audio-specific codec for faster processing
        '-y',  # Overwrite output file without asking
        output_file
    ]
    
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        return output_file
    else:
        error_message = stderr.decode()
        print(f"FFmpeg error: {error_message}")
        return None

# /trim_audio command handler
@Client.on_message(filters.command("trim_audio") & filters.reply)
async def trim_audio_handler(client, message):
    if not message.reply_to_message.audio:
        await message.reply("Please reply to an audio file with the command.")
        return

    try:
        # Notify the user that the download is starting
        status_message = await message.reply("Downloading the audio file...")

        # Extracting command arguments
        args = message.text.split()
        if len(args) < 3:
            await status_message.edit("Please provide the start and end times in the format: `/trim_audio start_time end_time`\nExample: `/trim_audio 00:00:10 00:00:30`")
            return

        start_time = args[1]
        end_time = args[2]

        # Downloading the audio file
        audio = message.reply_to_message.audio
        input_file = await client.download_media(audio)

        # Notify the user that the trimming is in progress
        await status_message.edit("Trimming the audio file...")

        output_file = f"trimmed_{audio.file_name}"

        # Trimming the audio
        trimmed_file = await trim_audio(input_file, output_file, start_time, end_time)
        if trimmed_file:
            # Notify the user that the upload is in progress
            await status_message.edit("Uploading the trimmed audio file...")

            await message.reply_document(trimmed_file)
            os.remove(trimmed_file)
            await status_message.delete()  # Delete the status message after completion
        else:
            await status_message.edit("An error occurred while trimming the audio. Please ensure the start and end times are correct.")
        
        # Clean up the input file
        os.remove(input_file)

    except Exception as e:
        await status_message.edit(f"An unexpected error occurred: {e}")
