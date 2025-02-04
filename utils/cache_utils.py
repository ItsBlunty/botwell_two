from datetime import datetime, timedelta, timezone
from discord.ext import commands, tasks
from utils.search_utils import search_results
import pickle
from pathlib import Path


class CacheUtils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def cleanup_old_messages(self):
        current_time = datetime.now(timezone.utc)
        week_ago = current_time - timedelta(days=7)
        
        expired = [msg_id for msg_id, msg_data in self.bot.message_cache.items()
                if msg_data['timestamp'] < week_ago]
        
        for msg_id in expired:
            del self.bot.message_cache[msg_id]
        
        return len(expired)

    def cleanup_old_searches(self):
        current_time = datetime.now()
        expired = [user_id for user_id, data in search_results.items()
                if current_time - data['timestamp'] > timedelta(minutes=120)]
        for user_id in expired:
            del search_results[user_id]

    async def load_cache(self):
        try:
            if Path('message_cache.pkl').exists():
                with open('message_cache.pkl', 'rb') as f:
                    self.bot.message_cache = pickle.load(f)
                print(f"Cache loaded: {len(self.bot.message_cache)} messages")
        except Exception as e:
            print(f"Error loading cache: {e}")
            self.bot.message_cache = {}

    @tasks.loop(minutes=5)
    async def auto_save_cache(self):
        try:
            with open('message_cache.pkl', 'wb') as f:
                pickle.dump(self.bot.message_cache, f)
        except Exception as e:
            print(f"Error auto-saving cache: {e}")

    @tasks.loop(hours=24)
    async def cleanup_message_cache(self):
        try:
            cleaned = self.cleanup_old_messages()
            print(f"Cleaned {cleaned} messages from cache")
        except Exception as e:
            print(f"Error cleaning message cache: {e}")

async def setup(bot):
    await bot.add_cog(CacheUtils(bot))