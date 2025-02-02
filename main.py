import discord
import pickle
from datetime import datetime
from pathlib import Path
from discord.ext import tasks
from dotenv import load_dotenv
import os
import signal
from utils.cache_utils import cleanup_old_messages
from bot import MyBot

load_dotenv()

bot = MyBot()
bot.remove_command('help')

@tasks.loop(minutes=5)
async def auto_save_cache():
    try:
        with open('message_cache.pkl', 'wb') as f:
            pickle.dump(bot.message_cache, f)
    except Exception as e:
        print(f"Error auto-saving cache: {e}")

@tasks.loop(hours=24)
async def cleanup_message_cache():
    try:
        cleaned = cleanup_old_messages(bot.message_cache)
        print(f"Cleaned {cleaned} messages from cache")
    except Exception as e:
        print(f"Error cleaning message cache: {e}")

async def load_cache():
    try:
        if Path('message_cache.pkl').exists():
            with open('message_cache.pkl', 'rb') as f:
                bot.message_cache = pickle.load(f)
            print(f"Cache loaded: {len(bot.message_cache)} messages")
    except Exception as e:
        print(f"Error loading cache: {e}")
        bot.message_cache = {}


def signal_handler(sig, frame):
    print("Shutdown initiated via Ctrl+C")
    
    if hasattr(bot, 'message_cache') and bot.message_cache:
        try:
            if Path('message_cache.pkl').exists():
                try:
                    with open('message_cache.pkl', 'rb') as f:
                        existing_cache = pickle.load(f)
                        existing_size = len(existing_cache)
                    
                    if len(bot.message_cache) >= existing_size:
                        with open('message_cache.pkl', 'wb') as f:
                            pickle.dump(bot.message_cache, f)
                        print(f"Final cache save completed: {len(bot.message_cache)} messages")
                    else:
                        print(f"Skipping save: Current cache ({len(bot.message_cache)}) smaller than stored cache ({existing_size})")
                except Exception as e:
                    print(f"Error checking existing cache: {e}")
            else:
                with open('message_cache.pkl', 'wb') as f:
                    pickle.dump(bot.message_cache, f)
                print(f"Final cache save completed: {len(bot.message_cache)} messages")
        except Exception as e:
            print(f"Error saving cache during shutdown: {e}")
    else:
        print("Cache not yet loaded or empty, skipping save")
    
    raise SystemExit


signal.signal(signal.SIGINT, signal_handler)

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')
    await load_cache()
    auto_save_cache.start()
    cleanup_message_cache.start()

@bot.event
async def on_raw_message_delete(payload):
    print(f"Delete event - Message ID: {payload.message_id}")
    
    cached_message = bot.message_cache.get(str(payload.message_id))
    
    if cached_message:
        print("Found message in cache")
        embed = discord.Embed(
            title="Message Deleted",
            description=f"In <#{cached_message['channel_id']}>",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Author", value=cached_message['author'], inline=False)
        embed.add_field(name="Content", value=cached_message['content'] or "No text content", inline=False)
        
        if cached_message['attachments']:
            attachments = "\n".join([f"[{filename}]({url})" for filename, url in cached_message['attachments']])
            embed.add_field(name="Attachments", value=attachments, inline=False)

        del bot.message_cache[str(payload.message_id)]

        log_channel = bot.get_channel(int(os.getenv('LOGGING_CHANNEL'))) 
        if log_channel:
            await log_channel.send(embed=embed)
    else:
        print(f"Message {payload.message_id} not found in cache")

@bot.event
async def on_disconnect():
    print("Bot disconnecting - saving cache...")
    await auto_save_cache()

bot.run(os.getenv('DISCORD_TOKEN'))