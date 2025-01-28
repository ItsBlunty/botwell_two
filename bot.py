import discord
from discord import TextStyle
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput, Button, View
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

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()
# bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
bot.remove_command('help')

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

class FeedbackModal(Modal, title='Feedback'):
    def __init__(self):
        super().__init__(title="Botwell Feedback")

        self.feedback = TextInput(
            label="Want anything changed? New Features?",
            style=TextStyle.paragraph,
            placeholder="Enter your feedback here...",
            required=True,
            max_length=300
        )
        self.add_item(self.feedback)
    
    async def on_submit(self, interaction: discord.Interaction):
        with open('feedback.txt', 'a') as f:
            f.write(f"{interaction.user.name}: {self.feedback.value}\n")
        
        await interaction.response.send_message("Thanks for writing in!", ephemeral=True)

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
async def botwell(ctx, *, query=None):
    cleanup_old_searches()
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
async def result(ctx, *, number=None):
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

@bot.command()
async def help(ctx):
    embed = discord.Embed(color=discord.Color.dark_purple(), title="Botwell Help")
    embed.add_field(name="Commands", value="Botwell has a variety of commands.\n\n`!botwell thing to search` - Search Bardwell's Youtube Channel for a topic and get 3 links to videos about that topic.\n`!more` - Gives you 3 more links from the list generated by `!botwell`\n`!result 1`,`!result 2`, and `!result 3` - Embeds the Video result you pick.\n`!help` - Shows this help screen!\n`!feedback` - Send in feedback about Botwell", inline=True)
    embed.add_field(name="", value="", inline=False)
    embed.set_footer(text="Made by itsblunty.")
    await ctx.send(embed=embed)

@bot.command()
async def feedback(ctx):
    button = Button(label="Give Feedback", style=discord.ButtonStyle.primary)

    async def button_callback(interaction):
        modal = FeedbackModal()
        await interaction.response.send_modal(modal)
    
    button.callback = button_callback
    view = View()
    view.add_item(button)
    await ctx.send("Click the button to give feedback about Botwell:", view=view)

bot.run(os.getenv('DISCORD_TOKEN'))