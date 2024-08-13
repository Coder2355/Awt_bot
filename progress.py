import math
import time
from pyrogram.types import Message

async def progress(current, total, message: Message, start, description):
    now = time.time()
    diff = now - start

    if diff < 2:  # Update progress every 2 seconds
        return

    percentage = current * 100 / total
    speed = current / diff
    time_to_completion = (total - current) / speed
    time_to_completion = round(time_to_completion)
    progress_str = "{0}{1} {2}%\n".format(
        ''.join(["■" for i in range(math.floor(percentage / 10))]),
        ''.join(["□" for i in range(10 - math.floor(percentage / 10))]),
        round(percentage, 2),
    )

    estimated_total_time = round(diff / current * total)
    try:
        await message.edit_text(
            "{}\n"
            "Progress: `{}`\n"
            "Speed: `{}`\n"
            "ETA: `{}`".format(
                description,
                progress_str,
                humanbytes(speed),
                time_formatter(time_to_completion),
            )
        )
    except Exception as e:
        print(f"Error updating progress: {e}")

def humanbytes(size):
    # Convert bytes to a human-readable format
    if not size:
        return ""
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'KiB', 2: 'MiB', 3: 'GiB', 4: 'TiB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}"

def time_formatter(seconds):
    # Convert seconds to a human-readable time format
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    if days != 0:
        result += f"{days}d"
    (hours, remainder) = divmod(remainder, 3600)
    if hours != 0:
        result += f"{hours}h"
    (minutes, seconds) = divmod(remainder, 60)
    if minutes != 0:
        result += f"{minutes}m"
    if seconds != 0:
        result += f"{seconds}s"
    return result
