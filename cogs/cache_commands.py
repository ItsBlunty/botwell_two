from discord.ext import commands
from utils.cache_utils import CacheUtils
from datetime import datetime, timedelta, timezone

class CacheCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.userid = 152656828193439744

    @commands.command(aliases=['cachesize','cache'])
    async def cacheinfo(self, ctx):
        if ctx.author.id == self.userid:
            cache_size = len(self.bot.message_cache)
            oldest_message = min(self.bot.message_cache.values(), key=lambda x: x['timestamp'])
            newest_message = max(self.bot.message_cache.values(), key=lambda x: x['timestamp'])
            
            await ctx.send(f"Cache contains {cache_size} messages\n"
                          f"Oldest message: {oldest_message['timestamp']}\n"
                          f"Newest message: {newest_message['timestamp']}")

    @commands.command(aliases=['cleanup','cleanmessages'])
    async def forcecleanup(self, ctx):
        if ctx.author.id == self.userid: 
            cache_utils_cog = self.bot.get_cog('CacheUtils')
            if cache_utils_cog:
                before_size = len(self.bot.message_cache)
                cleaned = cache_utils_cog.cleanup_old_messages()
                after_size = len(self.bot.message_cache)
                
                await ctx.send(f"Cache size before: {before_size}\n"
                            f"Messages cleaned: {cleaned}\n"
                            f"Cache size after: {after_size}")
            else:
                await ctx.send("CacheUtils cog not found")
            
    @commands.command(aliases=['addmessage'])
    async def addtestmessage(self, ctx, days_old: int):
        if ctx.author.id == self.userid: 
            old_timestamp = datetime.now(timezone.utc) - timedelta(days=days_old)
            
            test_message_id = f"test_{ctx.message.id}"
            self.bot.message_cache[test_message_id] = {
                'content': f"Test message {days_old} days old",
                'author': str(ctx.author),
                'author_id': ctx.author.id,
                'channel_id': ctx.channel.id,
                'timestamp': old_timestamp,
                'attachments': []
            }
            
            await ctx.send(f"Added test message to cache with timestamp: {old_timestamp}")

async def setup(bot):
    await bot.add_cog(CacheCommands(bot))