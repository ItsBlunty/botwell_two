import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True 
intents.message_content = True
intents.guild_messages = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.message_cache = {}

    async def setup_hook(self):
        await self.load_extension('utils.cache_utils')
        await self.load_extension('cogs.events')
        await self.load_extension('cogs.cache_commands')
        await self.load_extension('cogs.general_commands')
        await self.load_extension('cogs.search_commands')
        await self.load_extension('utils.newvideohandler')
        await self.tree.sync()