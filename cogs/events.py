from discord.ext import commands
from utils.storage import data_path
import signal
import pickle
from datetime import datetime
import os
import discord

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup_signal_handler()

    def setup_signal_handler(self):
        def signal_handler(sig, frame):
            print("Shutdown initiated")

            if hasattr(self.bot, 'message_cache') and self.bot.message_cache:
                try:
                    with open(data_path('message_cache.pkl'), 'wb') as f:
                        pickle.dump(self.bot.message_cache, f)
                    print(f"Final cache save completed: {len(self.bot.message_cache)} messages")
                except Exception as e:
                    print(f"Error saving cache during shutdown: {e}")
            else:
                print("Cache not yet loaded or empty, skipping save")

            raise SystemExit

        # SIGINT covers local Ctrl+C; SIGTERM is what Railway (and most
        # container platforms) send on shutdown/redeploy.
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

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

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} is now online!')
        cache_utils_cog = self.bot.get_cog('CacheUtils')
        if cache_utils_cog:
            await cache_utils_cog.load_cache()
            cache_utils_cog.auto_save_cache.start()
            cache_utils_cog.cleanup_message_cache.start()
        else:
            print("CacheUtils cog not found")

    @commands.Cog.listener()
    async def on_disconnect(self):
        print("Bot disconnecting - saving cache...")
        cache_utils_cog = self.bot.get_cog('CacheUtils')
        if cache_utils_cog:
            await cache_utils_cog.auto_save_cache()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        print(f"Delete event - Message ID: {payload.message_id}")
        
        cached_message = self.bot.message_cache.get(str(payload.message_id))
        
        if cached_message:
            print("Found message in cache")
            embed = discord.Embed(
                title="Message Deleted",
                description=f"In <#{cached_message['channel_id']}>",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="Author", value=cached_message['author'], inline=False)
            embed.add_field(name="Content", value=cached_message['content'] or "No text content", inline=False)
            
            if cached_message['attachments']:
                attachments = "\n".join([f"[{filename}]({url})" for filename, url in cached_message['attachments']])
                embed.add_field(name="Attachments", value=attachments, inline=False)

            del self.bot.message_cache[str(payload.message_id)]

            log_channel = self.bot.get_channel(int(os.getenv('LOGGING_CHANNEL')))
            if log_channel:
                await log_channel.send(embed=embed)
        else:
            print(f"Message {payload.message_id} not found in cache")

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        message_id = str(payload.message_id)
        cached_message = self.bot.message_cache.get(message_id)

        # We can only show "before" if we saw the original message.
        if not cached_message:
            print(f"Edit event - Message {payload.message_id} not found in cache")
            return

        # The raw payload can be partial (e.g. when Discord adds a link
        # preview embed it sends an update with no 'content' key). Only act
        # when the gateway gave us the new text.
        new_content = payload.data.get('content')
        if new_content is None:
            return

        old_content = cached_message['content']
        # Embed/preview updates and no-op edits leave the text unchanged.
        if new_content == old_content:
            return

        print(f"Edit event - Message ID: {payload.message_id}")

        embed = discord.Embed(
            title="Message Edited",
            description=f"In <#{cached_message['channel_id']}>",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )

        embed.add_field(name="Author", value=cached_message['author'], inline=False)
        embed.add_field(name="Original Message", value=self._field_value(old_content), inline=False)
        embed.add_field(name="Edited Message", value=self._field_value(new_content), inline=False)

        if payload.guild_id:
            jump_url = f"https://discord.com/channels/{payload.guild_id}/{cached_message['channel_id']}/{message_id}"
            embed.add_field(name="Jump", value=f"[Go to message]({jump_url})", inline=False)

        # Keep the cache current so a later edit compares against this version.
        cached_message['content'] = new_content

        log_channel = self.bot.get_channel(int(os.getenv('LOGGING_CHANNEL')))
        if log_channel:
            await log_channel.send(embed=embed)

    @staticmethod
    def _field_value(content):
        """Embed field values are capped at 1024 chars; keep us under it."""
        if not content:
            return "No text content"
        if len(content) > 1024:
            return content[:1021] + "..."
        return content

async def setup(bot):
    await bot.add_cog(EventHandler(bot))
