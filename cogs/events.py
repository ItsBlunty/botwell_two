from discord.ext import commands

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            message_id = str(message.id)
            self.bot.message_cache[message_id] = {
                'content': message.content,
                'author': str(message.author),
                'author_id': message.author.id,
                'channel_id': message.channel.id,
                'timestamp': message.created_at,
                'attachments': [(a.filename, a.url) for a in message.attachments]
            }

async def setup(bot):
    await bot.add_cog(EventHandler(bot))
