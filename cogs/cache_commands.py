from discord.ext import commands

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
            
async def setup(bot):
    await bot.add_cog(CacheCommands(bot))