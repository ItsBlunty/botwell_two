import discord
from discord.ext import commands
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

search_results = {}

load_dotenv()

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID = 'UCX3eufnI7A2I7IkKHZn8KSQ'

bot = commands.Bot(command_prefix='!', intents=intents)

def search_channel(query, channel_id, api_key):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)

        request = youtube.search().list(
            part='snippet',
            q=query,
            channelId=channel_id,
            type='video',
            maxResults=30
        )

        response = request.execute()
        return response
    except Exception as e:
        print(f"YouTube API error: {str(e)}")
        return None

def format_video_results(results, start_index):

    embed = discord.Embed(color=discord.Color.dark_purple())

    if len(results['items']) < start_index + 3:
        return None

    if results['items']:
        video = results['items'][start_index]
        video2 = results['items'][start_index + 1]
        video3 = results['items'][start_index + 2]
        videoname = video['snippet']['title']
        videoname2 = video2['snippet']['title']
        videoname3 = video3['snippet']['title']
        video_id = video['id']['videoId']
        video_id2 = video2['id']['videoId']
        video_id3 = video3['id']['videoId']
        url = f'https://www.youtube.com/watch?v={video_id}'
        url2 = f'https://www.youtube.com/watch?v={video_id2}'
        url3 = f'https://www.youtube.com/watch?v={video_id3}'

        embed.add_field(name="", value="For more results, respond `!more`\nTo show a specific result, respond `!result 2`\nPlease report any issues to <@152656828193439744>", inline=False)
        embed.add_field(name="Result 1", value="[" + videoname + "](" + url + ")", inline=True)
        embed.add_field(name="Result 2", value="[" + videoname2 + "](" + url2 + ")", inline=True)
        embed.add_field(name="Result 3", value="[" + videoname3 + "](" + url3 + ")", inline=True)
    
    return embed

def cleanup_old_searches():
    current_time = datetime.now()
    expired = [user_id for user_id, data in search_results.items()
               if current_time - data['timestamp'] > timedelta(minutes=120)]
    for user_id in expired:
        del search_results[user_id]

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def links(ctx):
    await ctx.send("You can find bardwell\'s links at:\nhttps://www.fpvknowitall.com/\nhttps://www.searchfpv.com\nhttps://www.youtube.com/channel/UCX3eufnI7A2I7IkKHZn8KSQ", suppress_embeds=True)

@bot.command()
async def botwell(ctx, *, query):
    cleanup_old_searches()
    if query == "":
        await ctx.send("You need to add a search term after `!botwell`!")
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

@bot.command()
async def more(ctx):
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

@bot.command()
async def result(ctx, *, number):
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

bot.run(os.getenv('DISCORD_TOKEN'))