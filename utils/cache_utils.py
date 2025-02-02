from datetime import datetime, timedelta, timezone
from discord.ext import commands
from utils.search_utils import search_results


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

async def setup(bot):
    await bot.add_cog(CacheUtils(bot))