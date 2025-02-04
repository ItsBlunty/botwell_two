import os
from dotenv import load_dotenv
from bot import MyBot

load_dotenv()

bot = MyBot()
bot.remove_command('help')

bot.run(os.getenv('DISCORD_TOKEN'))