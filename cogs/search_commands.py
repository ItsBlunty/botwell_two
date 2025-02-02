from discord.ext import commands
from utils.cache_utils import CacheUtils
from utils.search_utils import format_video_results, search_channel, search_results
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID = 'UCX3eufnI7A2I7IkKHZn8KSQ'

class SearchCommands(commands.Cog):

    @commands.command(aliases=['search'])
    async def botwell(self, ctx, *, query=None):
        CacheUtils.cleanup_old_searches(self)
        if query is None or query.strip() == "":
            await ctx.send('You need to add a search term after `!botwell`\nExample:`!botwell expresslrs binding` will search for "ExpressLRS Binding" on JB\'s channel.')
            return
        
        results = search_channel(query, CHANNEL_ID, YOUTUBE_API_KEY)

        if results is None:
            await ctx.send("Sorry, there was an error accessing YouTube. Please try again later.")
            return

        if not results['items']:
            await ctx.send("No videos found for that search!")
            return
        
        search_results[ctx.author.id] = {
            'results': results,
            'last_index': 3,
            'timestamp': datetime.now()
        }
        embed = format_video_results(results, 0)
        if embed is None:
            await ctx.send("No more results available!")
            return
        await ctx.send(embed=embed)

    @commands.command(aliases=['morevideos'])
    async def more(self, ctx):
        user_data = search_results.get(ctx.author.id)
        if not user_data:
            await ctx.send("No previous search found! Make an initial search with `!botwell`")
            return
        if user_data['last_index'] >= len(user_data['results']['items']):
            await ctx.send("No more results available!")
            return
        start_index = user_data['last_index']
        embed = format_video_results(user_data['results'], start_index)
        if embed is None:
            await ctx.send("No more results available!")
            return
        user_data['last_index'] += 3
        await ctx.send(embed=embed)

    @commands.command(aliases=['video'])
    async def result(self, ctx, *, number=None):
        if number is None or number.strip() == "":
            await ctx.send("We can't find that result! Maybe you mistyped? It should just be `!result 1` `!result 2` or `!result 3`")
            return
        user_data = search_results.get(ctx.author.id)
        if int(number) not in [1, 2, 3]:
            await ctx.send("We can't find that result! Maybe you mistyped? It should just be `!result 1` `!result 2` or `!result 3`")
            return
        try:
            numberint = 4 - int(number)
            adjustednumberint = user_data['last_index'] - numberint
        except ValueError:
            await ctx.send("We can't find that result! Maybe you mistyped? It should just be `!result 1` `!result 2` or `!result 3`")
            return
        if not user_data:
            await ctx.send("No previous search found! Make an initial search with `!botwell`")
            return
        video_id = user_data['results']['items'][adjustednumberint]['id']['videoId']
        await ctx.send(f'https://www.youtube.com/watch?v={video_id}')

async def setup(bot):
    await bot.add_cog(SearchCommands(bot))